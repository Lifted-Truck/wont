"""generate.py — quasi-random run generation over a parameter space.

Julian, 2026-07-08: "generate random or quasi-random runs testing different
parameters (cadence patterns, melodic walks, chord progressions) with a
satisfaction knob." This module owns the SAMPLING half — deterministically
turning a parameter space into a batch of client configs to audition. It does
NOT own generation itself: a client (Wend) turns each config into actual music
behind the Client seam below. wont stays client-agnostic (DESIGN.md §2).

Two samplers, both deterministic (seeded, no wall-clock — reproducible sweeps):
  - "quasi"  : a Halton low-discrepancy sequence — even coverage of the space
               with few samples (the good default for a listening budget: you
               hear the corners and the middle, not three clustered near-dupes).
  - "random" : a plain seeded RNG — for when you want IID draws (e.g. the
               synthetic recovery experiments of D11, where you plant a known
               utility over one axis and check the learner recovers it).

This is scaffolding: ParameterSpace + the samplers are real and tested; the
Client protocol is defined and the Wend adapter is a stub (clients/wend.py).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol


# ----------------------------------------------------------------------------
# Parameter space — the axes a sweep explores.
# ----------------------------------------------------------------------------

@dataclass
class ParameterSpace:
    """axis_name -> spec. Spec kinds:
        {"kind": "range",  "min": float, "max": float}          continuous
        {"kind": "int",    "min": int,   "max": int}            integer
        {"kind": "choice", "options": [...]}                    categorical
    A sample is a dict {axis_name: value}. Values map onto the CLIENT's config
    keys (opaque to wont) — see wend_starter_space() for the mapping to Wend.
    """
    axes: dict

    def validate(self) -> list[str]:
        errs = []
        for name, spec in self.axes.items():
            kind = spec.get("kind")
            if kind in ("range", "int"):
                if "min" not in spec or "max" not in spec or spec["min"] >= spec["max"]:
                    errs.append(f"axis {name!r}: {kind} needs min < max")
            elif kind == "choice":
                if not spec.get("options"):
                    errs.append(f"axis {name!r}: choice needs a non-empty options list")
            else:
                errs.append(f"axis {name!r}: unknown kind {kind!r}")
        return errs

    def _project(self, name: str, u: float):
        """Map a unit-interval coordinate u in [0,1) onto one axis's value."""
        spec = self.axes[name]
        kind = spec["kind"]
        if kind == "range":
            return spec["min"] + u * (spec["max"] - spec["min"])
        if kind == "int":
            n = spec["max"] - spec["min"] + 1
            return spec["min"] + min(int(u * n), n - 1)
        if kind == "choice":
            opts = spec["options"]
            return opts[min(int(u * len(opts)), len(opts) - 1)]
        raise ValueError(f"unknown axis kind {kind!r}")

    def to_dict(self) -> dict:
        return {"axes": self.axes}

    @classmethod
    def from_dict(cls, d: dict) -> "ParameterSpace":
        return cls(axes=d.get("axes", {}))


# ----------------------------------------------------------------------------
# Samplers — deterministic (bar-, not wall-clock-, driven).
# ----------------------------------------------------------------------------

def _halton(index: int, base: int) -> float:
    """The `index`-th value of the base-`base` Halton sequence, in [0,1)."""
    f, r = 1.0, 0.0
    i = index
    while i > 0:
        f /= base
        r += f * (i % base)
        i //= base
    return r


_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


def sample(space: ParameterSpace, n: int, *, method: str = "quasi", seed: int = 0):
    """Return `n` config dicts covering the space. Deterministic in (space, n,
    method, seed). Halton skips the first `seed+1` indices so `seed` still
    varies the quasi-random batch without losing low-discrepancy coverage."""
    names = sorted(space.axes)                 # stable axis order → reproducible
    out = []
    if method == "random":
        rng = random.Random(seed)
        for _ in range(n):
            out.append({name: space._project(name, rng.random()) for name in names})
        return out
    if method == "quasi":
        for k in range(n):
            idx = seed + k + 1                 # +1: Halton index 0 is degenerate
            coord = {name: _halton(idx, _PRIMES[j % len(_PRIMES)])
                     for j, name in enumerate(names)}
            out.append({name: space._project(name, coord[name]) for name in names})
        return out
    raise ValueError(f"unknown method {method!r} (want 'quasi' or 'random')")


# ----------------------------------------------------------------------------
# The client seam — wont samples; a client makes the music.
# ----------------------------------------------------------------------------

@dataclass
class GeneratedRun:
    """What a client returns for one config — everything a LabeledRun needs
    EXCEPT the satisfaction curve (which the listener supplies at audition)."""
    ruleset_text: str
    config: dict
    seed: int
    trace: dict                    # client-opaque (Wend: Trace.to_json())
    events: dict | None = None     # optional {part: [[onset,dur,midi,vel,voice]]}


class Client(Protocol):
    """The ONLY thing wont needs from a generator: turn a sampled config into a
    reproducible run. Wend is the first implementer (clients/wend.py). Keeps
    wont client-agnostic — no Wend import lives in the learner."""

    name: str
    version: str

    def generate_run(self, config: dict, seed: int) -> GeneratedRun: ...


def wend_starter_space() -> ParameterSpace:
    """An EXAMPLE space over Wend's harmony/feel knobs — Julian's three axes
    (cadence patterns, melodic walks, chord progressions) mapped to real Wend
    config keys. A starting point for scenarios to copy and narrow; the build
    agent should tune ranges against what actually sounds distinct.

        chord progressions -> harmonic_motion, chord_voices, voice_variation
        melodic walks      -> surface (arp style), topline_motif, bass_gravity
        cadence patterns   -> structure, surprise_budget  (+ ruleset choice,
                              which scenarios express via seed_rulesets)
    """
    return ParameterSpace(axes={
        "harmonic_motion": {"kind": "range", "min": 0.0, "max": 1.0},
        "chord_voices": {"kind": "range", "min": 3.0, "max": 6.0},
        "voice_variation": {"kind": "range", "min": 0.0, "max": 1.0},
        "surprise_budget": {"kind": "range", "min": 2.0, "max": 8.0},
        "structure": {"kind": "range", "min": 0.0, "max": 1.0},
        "surface": {"kind": "choice", "options":
                    ["block", "arp_up", "arp_updown", "arp_random"]},
    })
