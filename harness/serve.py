"""harness/serve.py — the scenario audition GUI server.

The loop Julian described (2026-07-08, D13): pick a scenario -> the harness
sweeps its parameter space into quasi-random runs -> Wend generates each ->
you audition and turn the satisfaction knob -> the lag-compensated curve is
saved as a scenario-tagged LabeledRun for the learner.

Everything wont-side is pure and tested (sampling, lag compensation, schema,
save); this file is the thin IO/orchestration adapter over it (global CLAUDE.md
architecture default: pure cores, thin IO edges). The Wend seam lives in
wont/clients/wend.py (the one Wend-importing module) — in-process transport
(D16). Stdlib http.server only; no framework.

Endpoints:
  GET  /                 -> index.html (the audition page)
  GET  /scenarios        -> [{scenario_id, description, target, capture,
                             parameter_space}]
  POST /sweep            -> {scenario_id, n, method, seed}
                            -> generate.sample -> WendClient.generate_run each
                            -> {runs: [{run_id, index, seed, config, bars,
                                        beats_per_bar, bpm, events, summary}]}
                            (full GeneratedRuns are cached server-side by run_id)
  POST /save             -> {run_id, samples, scopes}
                            -> capture.build_curve (the time-shift) ->
                               assemble LabeledRun -> loader.save into the
                               scenario's feedback_dir -> {saved, run_id}

Run on the Tonality venv from the synthetic-worlds parent dir so `import Wend`
resolves (the in-process transport):
    cd ~/Documents/Claude/synthetic-worlds/wont
    ~/Documents/Tonality/.venv/bin/python -m harness.serve
Port 8771 (Wend's playground is 8770; both can run at once).
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, ".."))          # .../wont
PARENT = os.path.normpath(os.path.join(REPO_ROOT, ".."))        # .../synthetic-worlds
SCENARIO_DIR = os.path.join(REPO_ROOT, "scenarios")
# Make `import wont` and `import Wend` both resolve when launched directly.
for _p in (REPO_ROOT, PARENT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# wont-side pieces — all pure, no stubs:
from wont.generate import ParameterSpace, sample          # deterministic sweep
from wont.scenario import Scenario                         # scenario loader
from wont.capture import build_curve                       # the time-shift
from wont.schema import LabeledRun, compute_run_id         # the data unit
from wont import loader                                    # save/load runs
from wont.clients.wend import WendClient, resolve_ruleset_text  # the Wend seam

PORT = 8771
DEFAULT_BPM = 96          # audition tempo (playback only; not part of the run id)


# ---------------------------------------------------------------------------
# Ready helpers (pure) — scenario -> configs, and run -> LabeledRun.
# ---------------------------------------------------------------------------

def load_scenarios() -> list:
    out = []
    if os.path.isdir(SCENARIO_DIR):
        for fn in sorted(os.listdir(SCENARIO_DIR)):
            if fn.endswith(".json"):
                with open(os.path.join(SCENARIO_DIR, fn)) as f:
                    out.append(Scenario.from_dict(json.load(f)))
    return out


def sweep(scenario: Scenario, n: int, method: str = "quasi", seed: int = 0) -> list:
    """Scenario space -> n client configs (deterministic in the args)."""
    space = ParameterSpace.from_dict(scenario.parameter_space)
    return sample(space, n, method=method, seed=seed)


def assemble_labeled_run(scenario: Scenario, generated, raw_dial_samples, scopes=None) -> LabeledRun:
    """Raw dial -> lag-compensated, scenario-tagged LabeledRun. `generated` is a
    generate.GeneratedRun from the client."""
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


def run_summary(generated) -> dict:
    """A small, UI-facing digest of a generated run (defensive over Wend's trace
    shape — the trace is client-opaque, so read it forgivingly)."""
    steps = generated.trace.get("steps", []) if isinstance(generated.trace, dict) else []
    end_key = None
    modulations = None
    if steps:
        snap = steps[-1].get("snapshot", {}) if isinstance(steps[-1], dict) else {}
        end_key = snap.get("key")
        modulations = snap.get("modulations")
    return {
        "notes": {part: len(evs) for part, evs in (generated.events or {}).items()},
        "bars": len(steps) or generated.config.get("bars"),
        "end_key": end_key,
        "modulations": modulations,
        "surface": generated.config.get("surface"),
    }


def _beats_per_bar(generated) -> int:
    """Playback grid. Wend meter is (num, den); default 4/4. Read the config's
    meter if present, else 4 — audition playback is fixed-meter v1 (meter
    excursions are rare and not worth complicating the player for)."""
    meter = generated.config.get("meter")
    if isinstance(meter, (list, tuple)) and meter:
        try:
            return int(meter[0])
        except (TypeError, ValueError):
            pass
    return 4


# ---------------------------------------------------------------------------
# Server state — a single-user local audition tool; in-memory is fine.
# ---------------------------------------------------------------------------

class Harness:
    def __init__(self):
        self._scenarios = {s.scenario_id: s for s in load_scenarios()}
        self._clients: dict = {}   # scenario_id -> WendClient
        self._runs: dict = {}      # run_id -> (scenario_id, GeneratedRun)

    def scenarios(self) -> list:
        return list(self._scenarios.values())

    def scenario(self, sid: str) -> Scenario:
        if sid not in self._scenarios:
            raise KeyError(sid)
        return self._scenarios[sid]

    def client_for(self, scenario: Scenario) -> WendClient:
        c = self._clients.get(scenario.scenario_id)
        if c is None:
            c = WendClient(resolve_ruleset_text(scenario.seed_rulesets))
            self._clients[scenario.scenario_id] = c
        return c

    def do_sweep(self, sid: str, n: int, method: str, seed: int) -> dict:
        scenario = self.scenario(sid)
        client = self.client_for(scenario)
        configs = sweep(scenario, n, method=method, seed=seed)
        runs = []
        for i, cfg in enumerate(configs):
            gen = client.generate_run(cfg, seed=seed + i)
            rid = compute_run_id(
                {"name": client.name, "version": client.version},
                gen.ruleset_text, gen.config, gen.seed,
            )
            self._runs[rid] = (sid, gen)
            runs.append({
                "run_id": rid,
                "index": i,
                "seed": gen.seed,
                "config": gen.config,
                "bars": gen.config.get("bars"),
                "beats_per_bar": _beats_per_bar(gen),
                "bpm": DEFAULT_BPM,
                "events": gen.events,
                "summary": run_summary(gen),
            })
        return {"scenario_id": sid, "count": len(runs), "runs": runs}

    def do_save(self, run_id: str, samples: list, scopes: list) -> dict:
        if run_id not in self._runs:
            raise KeyError(run_id)
        sid, gen = self._runs[run_id]
        scenario = self.scenario(sid)
        lr = assemble_labeled_run(scenario, gen, samples, scopes=scopes)
        # feedback_dir is scenario-relative to the repo root (convention:
        # scenarios/<id>/runs/); fall back to a per-scenario default.
        rel = scenario.feedback_dir or os.path.join("scenarios", sid, "runs")
        out_dir = os.path.join(REPO_ROOT, rel)
        path = loader.save_run(lr, out_dir)
        return {"saved": os.path.relpath(path, REPO_ROOT), "run_id": lr.run_id or lr.computed_run_id()}


# ---------------------------------------------------------------------------
# HTTP glue.
# ---------------------------------------------------------------------------

def _make_handler(harness: Harness):
    class Handler(BaseHTTPRequestHandler):
        server_version = "wont-harness/1.0"

        def _send(self, code: int, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _json(self, code: int, obj):
            self._send(code, json.dumps(obj).encode("utf-8"), "application/json")

        def _read_body(self) -> dict:
            n = int(self.headers.get("Content-Length", 0) or 0)
            if not n:
                return {}
            return json.loads(self.rfile.read(n).decode("utf-8"))

        def log_message(self, fmt, *args):   # quieter console
            sys.stderr.write("  %s\n" % (fmt % args))

        def do_HEAD(self):
            self.do_GET()   # _send already suppresses the body for HEAD

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                with open(os.path.join(HERE, "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
                return
            if self.path == "/scenarios":
                self._json(200, [{
                    "scenario_id": s.scenario_id,
                    "description": s.description,
                    "target": s.target,
                    "capture": s.capture,
                    "parameter_space": s.parameter_space,
                    "fingerprint": s.fingerprint(),
                } for s in harness.scenarios()])
                return
            self._json(404, {"error": f"no route {self.path}"})

        def do_POST(self):
            try:
                body = self._read_body()
            except json.JSONDecodeError as e:
                self._json(400, {"error": f"bad JSON: {e}"})
                return
            try:
                if self.path == "/sweep":
                    self._json(200, harness.do_sweep(
                        body["scenario_id"],
                        int(body.get("n", 8)),
                        str(body.get("method", "quasi")),
                        int(body.get("seed", 0)),
                    ))
                    return
                if self.path == "/save":
                    self._json(200, harness.do_save(
                        body["run_id"],
                        body.get("samples", []),
                        body.get("scopes", []),
                    ))
                    return
                self._json(404, {"error": f"no route {self.path}"})
            except KeyError as e:
                self._json(404, {"error": f"unknown id {e}"})
            except Exception as e:  # surface the real error to the UI, don't 500 blindly
                self._json(400, {"error": f"{type(e).__name__}: {e}"})

    return Handler


def main(port: int = PORT):
    harness = Harness()
    n_scen = len(harness.scenarios())
    server = ThreadingHTTPServer(("127.0.0.1", port), _make_handler(harness))
    print(f"wont audition harness on http://127.0.0.1:{port}  "
          f"({n_scen} scenario{'' if n_scen == 1 else 's'}: "
          f"{', '.join(s.scenario_id for s in harness.scenarios()) or 'none'})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
        server.shutdown()


if __name__ == "__main__":
    main()
