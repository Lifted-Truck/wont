"""clients/wend.py — Wend adapter for the generate.Client seam.

The ONE boundary module coupling wont to Wend (global CLAUDE.md shared-engine
rule 1: a single seam file is the only code that knows a peer's wire format;
everything downstream consumes normalized GeneratedRuns). Turns a sampled
config into a reproducible Wend run.

TRANSPORT: in-process import (DECISIONS.md D16). Wend is a sibling package in
the same `synthetic-worlds/` monorepo, and wont's interpreter is the Tonality
venv, which imports Wend cleanly (`from Wend... import ...`). The subprocess /
HTTP transports the scaffold weighed are a documented swap-in (see D16) for the
day wont must run without Wend's Python present; in-process is the honest v1 for
co-located siblings sharing a venv, and it hands back the in-memory
`result.events` / `assemble_parts` structures directly — no MIDI round-trip,
no fidelity loss, determinism airtight for the D11 recovery harness.

DETERMINISM: same (ruleset_text, config, seed) => byte-identical music (Wend's
own contract, __main__.py). `config` is the exact dict of Config-field overrides
applied on top of `ruleset_text`, so reproduction is just: re-parse the ruleset,
apply the overrides, set the seed, regenerate. That triple IS the LabeledRun's
run_id.
"""

from __future__ import annotations

import dataclasses
import json

from ..generate import GeneratedRun

# The one import door to Wend. If Wend is absent (wont running without its
# sibling), this raises at construction time with a clear message rather than
# failing deep in a sweep.
try:
    from Wend.oracle import make_oracle, parse_key
    from Wend.dsl import parse_ruleset, Config
    from Wend.engine import generate
    from Wend.parts import assemble_parts
    from Wend.__main__ import _BUILTIN_RULESET
    _WEND_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - exercised only when Wend is missing
    _WEND_IMPORT_ERROR = exc

# Config fields wont may legitimately override (verified against Wend's Config
# dataclass at wire-up). The sweep's axes (generate.wend_starter_space) are a
# subset; part toggles + bars round out a rich, reproducible audition.
_CONFIG_FIELDS = None  # populated lazily from the real dataclass


def _config_fields() -> set:
    global _CONFIG_FIELDS
    if _CONFIG_FIELDS is None:
        _CONFIG_FIELDS = {f.name for f in dataclasses.fields(Config)}
    return _CONFIG_FIELDS


# A part-full arrangement so the listener auditions music, not a bare chord
# spine. These are real Config booleans; overridable via a run's config.
_DEFAULT_ARRANGEMENT = {
    "bars": 16,
    "bass": True,
    "topline": True,
    "drums": True,
}


def resolve_ruleset_text(seed_rulesets: list) -> str:
    """Resolve a scenario's seed_rulesets (DESIGN.md §4 / scenario.py) to verbatim
    Wend DSL text — the reproducibility source of truth stored on every run.

    Recognizes:
      {"ref": "wend:builtin"}      -> Wend's built-in ruleset (__main__._BUILTIN_RULESET)
      {"ref": "<path.wend>"}       -> read that file
      {"dsl": "<verbatim text>"}   -> use inline DSL

    v1 uses the first entry. Empty / unrecognized -> the builtin (a working
    default beats a hard failure in an audition tool).
    """
    for entry in (seed_rulesets or []):
        if not isinstance(entry, dict):
            continue
        if "dsl" in entry and isinstance(entry["dsl"], str) and entry["dsl"].strip():
            return entry["dsl"]
        ref = entry.get("ref")
        if ref == "wend:builtin":
            return _BUILTIN_RULESET
        if isinstance(ref, str) and ref.endswith(".wend"):
            with open(ref, "r", encoding="utf-8") as fh:
                return fh.read()
    return _BUILTIN_RULESET


class WendClient:
    """Wend implementation of generate.Client. Constructed with the resolved
    ruleset text (from the scenario's seed_rulesets) so every run in a sweep
    reproduces against the same source."""

    name = "wend"

    def __init__(self, ruleset_text: str | None = None, *, oracle: str = "fallback"):
        if _WEND_IMPORT_ERROR is not None:
            raise RuntimeError(
                "WendClient needs Wend importable (in-process transport, D16). "
                f"Import failed: {_WEND_IMPORT_ERROR!r}. Run wont's server on the "
                "Tonality venv from the synthetic-worlds parent dir so `import Wend` "
                "resolves, or switch to the subprocess/HTTP transport (D16 swap-in)."
            )
        self.ruleset_text = ruleset_text if ruleset_text is not None else _BUILTIN_RULESET
        self.oracle_name = oracle
        self._oracle = make_oracle(oracle)
        # Wend's version isn't a package attribute; stamp the oracle flavor so the
        # LabeledRun.client records which generation surface produced it.
        self.version = f"0+{oracle}"

    def _effective_config(self, config: dict) -> dict:
        """Merge the sampled axes over the arrangement defaults, keeping only real
        Config fields. This dict is what gets stamped on the run AND re-applied to
        reproduce it — so it must be the complete override set."""
        fields = _config_fields()
        merged = {**_DEFAULT_ARRANGEMENT, **(config or {})}
        eff = {}
        for k, v in merged.items():
            if k not in fields:
                continue  # silently drop non-Config keys (e.g. a bookkeeping axis)
            # chord_voices is an int knob in Wend; sampled as float -> coerce.
            if k in ("bars", "chord_voices", "waypoints") and isinstance(v, float):
                v = int(round(v))
            eff[k] = v
        return eff

    def generate_run(self, config: dict, seed: int) -> GeneratedRun:
        eff = self._effective_config(config)
        rs = parse_ruleset(self.ruleset_text)
        for k, v in eff.items():
            setattr(rs.config, k, v)
        rs.config.seed = seed
        key0 = parse_key(rs.config.key)
        result = generate(self._oracle, rs, initial_key=key0)
        parts = assemble_parts(result, rs.config, self._oracle, seed)
        events = {
            name: [[float(e.start_beat), float(e.duration_beats),
                    int(e.midi), int(e.velocity)] for e in evs]
            for name, evs in parts.items() if evs
        }
        return GeneratedRun(
            ruleset_text=self.ruleset_text,
            config=eff,
            seed=seed,
            trace=json.loads(result.trace.to_json()),
            events=events,
        )
