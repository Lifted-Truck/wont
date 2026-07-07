"""schema.py — the labeled run: the unit of preference training data.

A LabeledRun wraps one generated composition (the client's reproducibility
fingerprint: ruleset text + config + seed + trace) with the satisfaction
curve a listener produced while it played. Designed so ANY Tonality client
can produce one: `ruleset_text` and `trace` are client-opaque blobs that
wont never parses — reproduction is the client's contract (Wend: seed +
ruleset regenerates bit-identically; the trace is Trace.to_json()).

Deliberately absent (see DESIGN.md §4): satisfaction thresholds (learner
policy, not data), engine analysis (derived downstream, never captured),
wall-clock reads in anything computed (a capture date may ride in `notes`
as inert provenance).

Validation is TOTAL — every error is collected and reported, mirroring
Tonality's `validate_ruleset` contract. Stdlib only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

SCHEMA_VERSION = "wont.labeled-run.1"

# Known pattern scopes (DESIGN.md §3). Open set: a `scope_session` naming an
# unknown scope is a warning-free pass (extensibility), but these are the
# scopes v1 slices by.
KNOWN_SCOPES = ("note_path", "rhythm", "harmony")


class ValidationError(ValueError):
    """Raised by LabeledRun.validate() carrying ALL problems found."""

    def __init__(self, errors: list[str]):
        self.errors = list(errors)
        super().__init__(
            "invalid LabeledRun (%d error%s):\n  - %s"
            % (len(errors), "" if len(errors) == 1 else "s", "\n  - ".join(errors))
        )


def _canonical_json(obj) -> str:
    """Deterministic JSON: sorted keys, no whitespace variance."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_run_id(client: dict, ruleset_text: str, config: dict, seed: int) -> str:
    """The reproducibility identity: sha256 over the generation fingerprint.

    Same fingerprint ⇒ same music (client determinism). Satisfaction and
    trace are deliberately excluded — two listening sessions over one run
    share a run_id (DECISIONS.md D4).
    """
    payload = _canonical_json(
        {
            "client": client,
            "ruleset_text": ruleset_text,
            "config": config,
            "seed": seed,
        }
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class SatisfactionCurve:
    """The dial signal: (bar, value) samples in the client's declared units.

    `samples` bars must be non-decreasing (a bar may carry several samples —
    a dial can move mid-bar); values must lie within [value_min, value_max].
    `lag_bars` records reaction-lag compensation ALREADY APPLIED by the
    client (0 = raw signal) — the learner must know either way (DESIGN.md
    §8.1: mislabeled lag is plausibly the loop's biggest noise source).
    """

    samples: list  # list[[bar:int, value:float]]
    value_min: float = 0.0
    value_max: float = 1.0
    lag_bars: int = 0

    def validate(self) -> list[str]:
        errs: list[str] = []
        if not isinstance(self.samples, list) or not self.samples:
            errs.append("satisfaction.samples must be a non-empty list")
            return errs
        if not (isinstance(self.value_min, (int, float)) and isinstance(self.value_max, (int, float))):
            errs.append("satisfaction.value_min/value_max must be numbers")
            return errs
        if not self.value_min < self.value_max:
            errs.append(
                f"satisfaction.value_min ({self.value_min}) must be < value_max ({self.value_max})"
            )
        if not isinstance(self.lag_bars, int) or self.lag_bars < 0:
            errs.append(f"satisfaction.lag_bars must be a non-negative int, got {self.lag_bars!r}")
        prev_bar = None
        for i, pair in enumerate(self.samples):
            if (
                not isinstance(pair, (list, tuple))
                or len(pair) != 2
                or not isinstance(pair[0], int)
                or isinstance(pair[0], bool)
                or not isinstance(pair[1], (int, float))
                or isinstance(pair[1], bool)
            ):
                errs.append(f"satisfaction.samples[{i}] must be [bar:int, value:number], got {pair!r}")
                continue
            bar, value = pair
            if bar < 0:
                errs.append(f"satisfaction.samples[{i}] bar must be >= 0, got {bar}")
            if prev_bar is not None and bar < prev_bar:
                errs.append(
                    f"satisfaction.samples[{i}] bars must be non-decreasing ({bar} after {prev_bar})"
                )
            if isinstance(self.value_min, (int, float)) and isinstance(self.value_max, (int, float)):
                if not (self.value_min <= value <= self.value_max):
                    errs.append(
                        f"satisfaction.samples[{i}] value {value} outside declared range "
                        f"[{self.value_min}, {self.value_max}]"
                    )
            prev_bar = bar
        return errs

    def to_dict(self) -> dict:
        return {
            "samples": [[int(b), float(v)] for b, v in self.samples],
            "value_min": self.value_min,
            "value_max": self.value_max,
            "lag_bars": self.lag_bars,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SatisfactionCurve":
        return cls(
            samples=d.get("samples", []),
            value_min=d.get("value_min", 0.0),
            value_max=d.get("value_max", 1.0),
            lag_bars=d.get("lag_bars", 0),
        )


@dataclass
class LabeledRun:
    """One generated composition + one listener's satisfaction over it."""

    client: dict  # {"name": str, "version": str}
    ruleset_text: str  # verbatim client ruleset — opaque to wont
    config: dict  # client's full parameterization — opaque to wont
    seed: int
    trace: dict  # client-opaque trace JSON (Wend: json.loads(Trace.to_json()))
    satisfaction: SatisfactionCurve
    engine_pins: dict = field(default_factory=dict)  # {"key_profile": "kk-1982.1", ...}
    scope_session: str | None = None  # set when auditioned for ONE scope (DESIGN §7b)
    events: dict | None = None  # optional {part: [[onset_beats, dur_beats, midi, vel, voice], ...]}
    notes: list = field(default_factory=list)
    run_id: str | None = None  # derived if absent; verified if present
    schema_version: str = SCHEMA_VERSION

    # -- identity -----------------------------------------------------------

    def computed_run_id(self) -> str:
        return compute_run_id(self.client, self.ruleset_text, self.config, self.seed)

    # -- validation (total) -------------------------------------------------

    def validate(self) -> "LabeledRun":
        """Raise ValidationError carrying EVERY problem, or return self."""
        errs: list[str] = []

        if self.schema_version != SCHEMA_VERSION:
            errs.append(
                f"schema_version {self.schema_version!r} is not {SCHEMA_VERSION!r} "
                "(unknown versions are not silently accepted)"
            )
        if not isinstance(self.client, dict) or not isinstance(self.client.get("name"), str) or not self.client.get("name"):
            errs.append('client must be a dict with a non-empty "name" (and ideally "version")')
        if not isinstance(self.ruleset_text, str) or not self.ruleset_text:
            errs.append("ruleset_text must be a non-empty string (verbatim client ruleset)")
        if not isinstance(self.config, dict):
            errs.append(f"config must be a JSON object, got {type(self.config).__name__}")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool):
            errs.append(f"seed must be an int, got {self.seed!r}")
        if not isinstance(self.trace, dict):
            errs.append(f"trace must be a JSON object, got {type(self.trace).__name__}")
        if isinstance(self.satisfaction, SatisfactionCurve):
            errs.extend(self.satisfaction.validate())
        else:
            errs.append("satisfaction must be a SatisfactionCurve")
        if not isinstance(self.engine_pins, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in self.engine_pins.items()
        ):
            errs.append("engine_pins must map prior-name strings to version strings")
        if self.scope_session is not None and (
            not isinstance(self.scope_session, str) or not self.scope_session
        ):
            errs.append(f"scope_session must be a non-empty string or None, got {self.scope_session!r}")
        if self.events is not None:
            errs.extend(self._validate_events())
        if not isinstance(self.notes, list):
            errs.append("notes must be a list")

        # run_id: verify only when the fingerprint fields are themselves valid,
        # otherwise the mismatch message is just noise on top of the real error.
        fingerprint_ok = not any(
            e.startswith(("client ", "ruleset_text", "config ", "seed "))
            for e in errs
        )
        if self.run_id is not None and fingerprint_ok:
            expected = self.computed_run_id()
            if self.run_id != expected:
                errs.append(
                    f"run_id {self.run_id!r} does not match the fingerprint "
                    f"(expected {expected!r}) — fingerprint fields changed after id assignment?"
                )

        if errs:
            raise ValidationError(errs)
        return self

    def _validate_events(self) -> list[str]:
        errs: list[str] = []
        if not isinstance(self.events, dict):
            return [f"events must be a dict of part -> event list, got {type(self.events).__name__}"]
        for part, evs in self.events.items():
            if not isinstance(part, str) or not isinstance(evs, list):
                errs.append(f"events[{part!r}] must be a list under a string part name")
                continue
            for i, ev in enumerate(evs):
                if not isinstance(ev, (list, tuple)) or not (3 <= len(ev) <= 5):
                    errs.append(
                        f"events[{part!r}][{i}] must be [onset_beats, dur_beats, midi(, velocity, voice)], got {ev!r}"
                    )
                    continue
                onset, dur, midi = ev[0], ev[1], ev[2]
                if not isinstance(onset, (int, float)) or onset < 0:
                    errs.append(f"events[{part!r}][{i}] onset_beats must be >= 0, got {onset!r}")
                if not isinstance(dur, (int, float)) or dur <= 0:
                    errs.append(f"events[{part!r}][{i}] dur_beats must be > 0, got {dur!r}")
                if not isinstance(midi, int) or isinstance(midi, bool) or not (0 <= midi <= 127):
                    errs.append(f"events[{part!r}][{i}] midi must be an int in 0..127, got {midi!r}")
        return errs

    # -- JSON round-trip ------------------------------------------------------

    def to_dict(self) -> dict:
        d = {
            "schema_version": self.schema_version,
            "run_id": self.run_id if self.run_id is not None else self.computed_run_id(),
            "client": self.client,
            "engine_pins": self.engine_pins,
            "ruleset_text": self.ruleset_text,
            "config": self.config,
            "seed": self.seed,
            "trace": self.trace,
            "satisfaction": self.satisfaction.to_dict(),
            "scope_session": self.scope_session,
            "notes": self.notes,
        }
        if self.events is not None:
            d["events"] = self.events
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, d: dict) -> "LabeledRun":
        return cls(
            schema_version=d.get("schema_version", "<missing>"),
            run_id=d.get("run_id"),
            client=d.get("client", {}),
            engine_pins=d.get("engine_pins", {}),
            ruleset_text=d.get("ruleset_text", ""),
            config=d.get("config", {}),
            seed=d.get("seed", None),
            trace=d.get("trace", {}),
            satisfaction=SatisfactionCurve.from_dict(d.get("satisfaction", {})),
            scope_session=d.get("scope_session"),
            events=d.get("events"),
            notes=d.get("notes", []),
        )

    @classmethod
    def from_json(cls, text: str) -> "LabeledRun":
        return cls.from_dict(json.loads(text))
