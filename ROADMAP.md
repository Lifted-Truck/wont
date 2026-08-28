# wont — ROADMAP (phase-gated)

> The **sequencing + gate authority** for wont: what is built, in what order, and
> the gate each phase must clear. Phases advance only when their exit criterion is
> met, and **gates are never weakened to pass** (oracle discipline). This owns the
> *what/when*; [DESIGN.md](DESIGN.md) owns the *how* (design of record);
> [DECISIONS.md](DECISIONS.md) is the immutable log. **Last verified: 2026-07-10.**

## Non-negotiables (hold in every phase)

- **AI/deterministic boundary** — training is offline; artifacts are versioned +
  provenance-stamped; a pinned artifact + seed reproduces exactly; nothing learns
  online inside a generator.
- **One `mts` boundary** (`wont/engine.py`) and **one Wend seam** (`wont/clients/`).
- **Classical ML only** (Markov / bandit / logistic). Feature vocabulary is
  Tonality's, never bespoke.
- **Statistical honesty** — liked/disliked mined as separate corpora and
  *contrasted*; never duplicate spans; `pieces = runs` (one pooled pseudo-piece
  per `(run, scope)`, [L0004] / response-2).

---

## Phase 1 — Audition harness ✅ DONE (2026-07-08)

Generate/sweep (quasi + random, seeded), `WendClient` in-process (D16), the
satisfaction-dial capture with the reaction-lag time-shift (D15), scenario-tagged
`LabeledRun` save; scenario schema frozen (D17). Server on `:8771`; 32 tests green.

**Exit criterion (met):** end-to-end sweep → audition → save yields a valid
scenario-tagged `LabeledRun`, verified in-browser and in `tests/test_harness.py`.

---

## ⛔ GATE — the learner phase

Build the learner (DESIGN §5–§9) and `wont/engine.py` only when **both** hold
(CLAUDE.md; D2 dialogue-first — this gate is explicit and on the record):

1. **Tonality intake dialogue resolved** — ✅ brief/response (registered, gap-20
   consumer of record), brief-2/response-2 (per-run pooling), the notices
   (Markov/gap-14 vocabulary, field-manifest, firings, readout boundary).
2. **Julian approves the start** — ⬜ *pending.*

---

## Phase 2 — Synthetic-recovery harness (NEXT, per D11)

The learner's **first** build — validates the ML with **zero human listening**.
Plant a *known* preference over one swept axis (Wend determinism makes hundreds of
runs cheap) → fabricate labeled runs carrying that utility → train → verify the
learner **recovers** it before it ever touches real ears.

Builds:
- **`wont/engine.py`** — the sole `mts` importer (the boundary module).
- **slicer** — curve → liked/disliked spans (session-median + hysteresis, §8).
- **corpus builder** — one pooled pseudo-piece per `(run, scope)`, never per-span
  ([L0004]); each scope its own corpus.
- **contrast** — `induce_rules(liked)` / `induce_rules(disliked)` →
  `compare_rulesets`; `cross_entropy` as the recovery metric (**held-out split by
  run**, response-2).

**Exit criterion (Layer-0, CI-blocking):** on a seeded synthetic corpus the
recovered contrast correlates with the injected utility above a **pre-registered**
threshold, reproducibly. No model calls in the gate.

---

## Phase 3 — Real-capture loop (v1 threshold + contrast, DESIGN §9)

Capture real sessions via the harness → slice → per-`(run, scope)` corpora →
`induce_rules` → `compare_rulesets` → emit a **`BiasArtifact`** (§5) + the
**readout** (§6) → **seal** the corpus (D19 tier 2: `corpora/<scenario>/<seal>/` +
its hash manifest). Below-floor corpora emit a readout but **no artifact**.

**Exit criterion:** a fresh agent with only `mts` + the readout reproduces our
numbers exactly (§6 design test) — deterministic engine + pinned priors + committed
corpora.

---

## Phase 4 — Close the loop

Apply a `BiasArtifact` in Wend deterministically (pinned, seeded); confirm the top
contrast finding with a **variation-replay ablation** (§7a / §9 step 8).

**Exit criterion:** variation replay shows the predicted satisfaction delta on the
varied scope.

---

## Backlog — trigger-gated (do NOT build until the trigger fires)

| Item | Trigger | Ref |
|---|---|---|
| Markov/harmony scope (`build_transition_matrix` contrast); follow-up brief for the symmetric `compare_transition_matrices` slice (wont named consumer) | harmony scope goes Markov | [L0003], brief-2 |
| Graded sample-weights (gap 20) | binary liked/disliked demonstrably too coarse on real curves | DESIGN §1/§9 |
| Bandit over parameterizations | enough sessions that exploration policy matters | §9 |
| Per-scope logistic saliency (firings hook shipped) | corpora large enough to split | [L0003], §7c |
| Clustered / mixed-effects (`run_id` grouping key) | same-scope repeats, or a cross-scope joint model | response-2 |

## Open policy knobs — decided AT Phase-2 build, not before (§8)

Slice threshold + hysteresis; min-span length; value normalization (v1:
session-median). Reaction lag is settled (fixed 2 bars, D15).
