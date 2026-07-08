# wont — build-agent handoff

> Prepared 2026-07-08 by the Wend agent, at Julian's direction, as the launch
> pad for a dedicated wont build-agent. Read this, then `DESIGN.md` (the deep
> design) and `DECISIONS.md` (D1–D15, the binding choices). Everything here
> respects those; where this brief adds something new it is recorded as a
> decision (D13–D15). **This is scaffolding, not the build** — the concrete
> pure modules are done and tested; the GUI, the client wiring, and the learner
> are yours.

## Your mission (Julian, 2026-07-08)

Build wont its **own GUI + test harness** that:
1. generates **random / quasi-random runs** sweeping parameters — cadence
   patterns, melodic walks, chord progressions — each auditioned with a
   **satisfaction knob**;
2. supports **scenarios**: a named training context (e.g. a genre) that starts
   from **predefined Tonality/Wend rulesets** and refines to Julian's taste;
3. **saves feedback tagged to its scenario**, so it can be recalled for reuse in
   Wend and other tools without bleeding across contexts.

Then it's out of the Wend agent's hands — you own it from here.

## What already runs (below the seam — no stubs)

| module | status | what it gives you |
|---|---|---|
| `wont/schema.py` | frozen `.1` | `LabeledRun` — the training-data unit (client-agnostic, total validation) |
| `wont/loader.py` | done | save/load a run or a corpus directory |
| `wont/capture.py` | **done** | the **time-shift**: raw dial → lag-compensated, schema-valid `SatisfactionCurve` (D15) |
| `wont/scenario.py` | **draft** | `Scenario` — the scenario schema (validated, round-trip). `.1-draft` — finalize it |
| `wont/generate.py` | **done** | `ParameterSpace` + deterministic quasi/random `sample()`; the `Client` seam; `wend_starter_space()` |
| `scenarios/lofi-lounge.json` | example | a worked scenario — copy and retarget |

Run the tests: `~/Documents/Tonality/.venv/bin/python -m pytest tests/ -q`

## What you build (the stubs + the UI)

1. **`wont/clients/wend.py` — `WendClient.generate_run`.** The one seam to Wend.
   Pick a transport (in-process import vs subprocess/HTTP `python -m Wend
   --serve`; the docstring weighs both — the shared-engine protocol prefers the
   decoupled subprocess/HTTP contract). Map a sampled config onto Wend config
   keys; return a `GeneratedRun` whose `(ruleset_text, config, seed)`
   regenerate identical music.
2. **`harness/serve.py` — the HTTP server.** The orchestration + the ready
   helpers (`sweep`, `assemble_labeled_run`) are written; build the server
   around them (mirror `Wend/serve.py`). Endpoints: `/scenarios`, `/sweep`,
   `/save`. Use a different port than Wend (8771).
3. **`harness/index.html` — the audition UI.** A skeleton exists (dial +
   lag-shifted graph + scenario picker + the loop wired to TODOs). Build out
   playback (WebAudio, as Wend does) and the real generate/save calls.
4. **The learner** (`DESIGN.md` §5–§9) — still design-only, still gated on
   dialogue. **Do NOT jump to it.** Per **D11**, the FIRST learner-phase build
   is the **synthetic recovery harness**: plant a known preference over one
   swept axis (Wend's determinism makes hundreds of runs cheap), train, verify
   the learner recovers it before it ever touches real ears. The `generate.py`
   `"random"` sampler + `capture.py` are exactly the primitives for that.

## Non-negotiables (inherited — see DESIGN.md §1, global CLAUDE.md)

- **AI/deterministic boundary.** Training is offline; the learner emits
  versioned, provenance-stamped artifacts; a consumer applies a pinned artifact
  deterministically. Nothing learns online. Samplers are seeded, no wall-clock.
- **Feature vocabulary is Tonality's**, not bespoke. The `mts` boundary lives in
  ONE file (`wont/engine.py`, still unwritten); client adapters stay in
  `wont/clients/`. Don't reimplement engine analysis.
- **Classical ML only** (Markov / bandit / logistic). Interpretable by design.
- **Statistical honesty** (D6, DESIGN §1): liked/disliked mined as *separate*
  corpora and contrasted; never duplicate spans to fake weights.
- **Scopes are optional side-information (D12), not the mechanism.** Global
  whole-composition rating is the default sufficient path.

## The three new things this handoff introduces

- **D13** — wont gets its OWN GUI + generator (capture was Wend-side; now wont
  drives sweeps and auditions directly).
- **D14** — the **scenario** as a first-class training context; feedback tagged
  by `scenario_id` (rides in `LabeledRun.notes` so the frozen schema stays
  client-agnostic) → a scenario-scoped bias artifact reusable by Wend.
- **D15** — the **satisfaction time-shift**: the curve is shifted earlier by the
  reaction lag so labels align to their cause. Implemented in `capture.py`
  (default 2 bars, D8), drawn shifted in the GUI, `lag_bars` stamped for the
  learner. Learner-side lag *search* stays a documented hook (DESIGN §8.1).

## Reuse contract (why scenarios matter)

A scenario's accumulated runs → a `BiasArtifact` (DESIGN §5) tagged with the
`scenario_id` + the scenario `fingerprint()`. Wend (or any client) requests "the
lofi-lounge bias" and applies it deterministically for that context. Keep the
tag on every run and the fingerprint on every artifact — that provenance chain
is what makes the feedback recallable and auditable.
