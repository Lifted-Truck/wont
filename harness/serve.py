"""harness/serve.py — the scenario audition GUI (SCAFFOLD orchestration).

The loop Julian described (2026-07-08): pick a scenario -> the harness sweeps
its parameter space into quasi-random runs -> a client (Wend) generates each ->
you audition and turn the satisfaction knob -> the lag-compensated curve is
saved as a scenario-tagged LabeledRun for the learner. This file is the
ORCHESTRATION scaffold: the flow and seams are laid out; the build agent fills
the generation/playback wiring and builds out the real UI (it owns the GUI).

Flow (each endpoint marked TODO is the agent's to implement):
  GET  /                 -> serve index.html (the audition page)
  GET  /scenarios        -> list scenarios/*.json  (Scenario.from_dict)
  POST /sweep            -> {scenario_id, n, method, seed} ->
                            generate.sample(space, n, method, seed)  [pure, ready]
                            -> for each config: WendClient.generate_run(config, seed)
                               [clients/wend.py — STUB] -> return runs + traces
  POST /save             -> {run fingerprint, raw dial samples, scopes} ->
                            capture.build_curve(samples, lag_bars from scenario)
                               [ready] -> assemble LabeledRun [schema.py, ready]
                               -> loader.save into scenarios/<id>/runs/ [ready]

Only the CLIENT generation step and the browser UI are unbuilt — everything
wont-side (sampling, lag compensation, schema, save) is already runnable below
the seam. Run from this dir with the Tonality venv (carries mts if a client
needs it). Mirrors Wend's playground (python -m Wend --serve, port 8770); pick a
different port here (e.g. 8771) so both can run at once.
"""

from __future__ import annotations

import json
import os

# wont-side pieces that are ALREADY runnable (no stubs):
from wont.generate import ParameterSpace, sample         # deterministic sweep
from wont.scenario import Scenario                        # scenario loader
from wont.capture import build_curve                      # the time-shift
from wont.schema import LabeledRun, SatisfactionCurve     # the data unit
from wont import loader                                   # save/load runs

PORT = 8771
HERE = os.path.dirname(os.path.abspath(__file__))
SCENARIO_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "scenarios"))


def load_scenarios() -> list:
    out = []
    if os.path.isdir(SCENARIO_DIR):
        for fn in sorted(os.listdir(SCENARIO_DIR)):
            if fn.endswith(".json"):
                with open(os.path.join(SCENARIO_DIR, fn)) as f:
                    out.append(Scenario.from_dict(json.load(f)))
    return out


def sweep(scenario: Scenario, n: int, method: str = "quasi", seed: int = 0) -> list:
    """The ready half of /sweep: scenario space -> n client configs. The build
    agent feeds each config through WendClient.generate_run to get playable
    music (clients/wend.py)."""
    space = ParameterSpace.from_dict(scenario.parameter_space)
    return sample(space, n, method=method, seed=seed)


def assemble_labeled_run(scenario: Scenario, generated, raw_dial_samples, scopes=None) -> LabeledRun:
    """The ready half of /save: raw dial -> lag-compensated, scenario-tagged
    LabeledRun. `generated` is a generate.GeneratedRun from the client."""
    cap = scenario.capture
    curve = build_curve(
        raw_dial_samples,
        value_min=cap.get("value_min", -1.0),
        value_max=cap.get("value_max", 1.0),
        lag_bars=cap.get("lag_bars", 2),
    )
    return LabeledRun(
        client=dict(scenario.client),
        ruleset_text=generated.ruleset_text,
        config=generated.config,
        seed=generated.seed,
        trace=generated.trace,
        satisfaction=curve,
        engine_pins=dict(scenario.engine_pins),
        scopes=list(scopes or []),
        events=generated.events,
        # scenario tag rides in notes so the frozen labeled-run schema stays
        # client-agnostic (the reuse handle; DECISIONS.md D14).
        notes=[f"scenario:{scenario.scenario_id}", f"scenario_fp:{scenario.fingerprint()}"],
    )


def main():  # pragma: no cover — the agent builds the HTTP server here
    raise NotImplementedError(
        "harness/serve.py is an orchestration scaffold. Build the HTTP server "
        "(mirror Wend/serve.py): serve index.html, wire /scenarios /sweep /save "
        "to the ready helpers above, and implement WendClient.generate_run so "
        "/sweep returns playable runs. The wont-side helpers (sweep, "
        "assemble_labeled_run) already run — only client generation + the UI "
        "remain."
    )


if __name__ == "__main__":  # pragma: no cover
    main()
