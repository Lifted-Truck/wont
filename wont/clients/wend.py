"""clients/wend.py — Wend adapter for the generate.Client seam (STUB).

Turns a sampled config into a reproducible Wend run. This is a scaffold: the
build agent wires it to Wend for real. Two viable transports — pick per the
latency/coupling trade the agent prefers:

  (A) in-process import  — `from Wend.dsl import parse_ruleset` /
      `from Wend.engine import generate` (siblings on disk). Fastest; couples
      wont to Wend's Python API and version.
  (B) subprocess / HTTP  — drive `python -m Wend --serve` (port 8770) POST
      /generate, or shell `python -m Wend --out <dir>` and read walk.mid +
      trace.json. Slower; keeps wont decoupled from Wend internals (preferred
      by the shared-engine protocol — treat the client as a data contract, not
      a library).

Whichever transport: the adapter must return a GeneratedRun whose (ruleset_text,
config, seed) regenerate the SAME music on Wend — that identity is the
LabeledRun's run_id. Map the sampled axis dict onto Wend config keys 1:1
(generate.wend_starter_space names real Wend keys), pick a seed per run, and
capture Wend's Trace.to_json() as the opaque trace (+ events if embedding).

Run Wend from the parent dir `~/Documents/Claude/synthetic-worlds/` as
`python -m Wend` (capital W); the shell cwd resets between calls (Wend gotcha).
"""

from __future__ import annotations

from ..generate import GeneratedRun


class WendClient:
    name = "wend"
    version = "0"          # TODO: read Wend's real version at wire-up

    def __init__(self, transport: str = "subprocess"):
        # TODO(agent): choose 'import' or 'subprocess'/'http' per notes above.
        self.transport = transport

    def generate_run(self, config: dict, seed: int) -> GeneratedRun:
        raise NotImplementedError(
            "WendClient.generate_run is a scaffold. Wire it to Wend per the "
            "module docstring: map `config` onto Wend config keys, generate with "
            "`seed`, and return a GeneratedRun carrying ruleset_text + config + "
            "seed + Trace.to_json() (and events if embedding). The (ruleset_text, "
            "config, seed) triple must regenerate identical music."
        )
