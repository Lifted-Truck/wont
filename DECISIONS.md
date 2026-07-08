# wont — decision log (append-only)

## D1 — 2026-07-07 — provisional name "wont"

Chosen by the scaffolding agent (Julian could not be asked mid-task; the
brief required a provisional pick). Rationale: archaic monosyllable pairing
with sibling "Wend" — Wend walks, wont is the learned habit/preference.
Alternatives recorded in README (fain, lief). **Awaiting Julian's approval;**
rename is cheap now and only gets more expensive.

## D2 — 2026-07-07 — dialogue-first: schema/loader is the only code

Per Julian's explicit directive (dialogue before concrete decisions), the
only implemented slice is the labeled-run schema + loader + tests — the part
that is reversible and safe pre-dialogue (any client needs to produce runs
regardless of learner internals). The learner, bias-artifact code, readout
writer, and the `mts` boundary module are design-only until the Tonality
intake response lands and Julian reviews DESIGN.md.

## D3 — 2026-07-07 — labeled-run core is client-agnostic; trace is opaque

The schema requires only (client id, ruleset_text, config, seed, trace JSON,
satisfaction curve). `ruleset_text` and `trace` are client-opaque blobs —
wont never parses them; reproduction is the client's contract. This is what
makes the schema producible by ANY Tonality client, not just Wend. Engine
analysis is derived downstream, never captured in the run.

## D4 — 2026-07-07 — run_id is a content hash over (client, ruleset_text, config, seed)

The reproducibility fingerprint IS the identity: same fingerprint, same
music (client determinism). Satisfaction/trace are excluded — two listening
sessions over the same generated run share a run identity but are distinct
LabeledRun files (distinguished by path/collection, not id). Revisit if a
session_id proves necessary.

## D5 — 2026-07-07 — Tonality intake branch cut from main

`wont-intake-brief` branches from Tonality `main`, not from the unmerged
`wend-brief3-response` — a new directory can't conflict, and the brief cites
response-3 by path (it lands on main when PR merges). No push, no PR — left
for Julian's review per the task directive.

## D6 — 2026-07-07 — validation is total

Schema validation collects every error rather than failing fast, mirroring
Tonality's `validate_ruleset` contract (built for machine-generated input,
where "fix one, resubmit, find the next" is a bad loop).

## D7 — 2026-07-07 — knowledge loop integrated (fork choices)

Per Julian's directive, the self-improving knowledge loop
(~/Documents/Claude/integrate-knowledge-loop.prompt.md) is installed:
protocol block in CLAUDE.md, INDEX.md + LIBRARY.md created, seeded with one
session-real lesson (L0001, the Tonality-venv interpreter fact). Fork
choices (Julian to review): (a) candidate lessons INLINE in LIBRARY tagged
by tier — one retrieval surface beats a QUARANTINE.md in a one-contributor
repo; (b) VOLUNTARY reflection — no hook infrastructure yet in a design-phase
repo; revisit if lessons get missed. Tag vocabulary is domain-tuned:
stat-soundness, credit-assignment, labeled-run-schema, tonality-channel,
artifact-contract, env-tooling.

## D8 — Approvals from the 2026-07-07 design dialogue (Julian)

- **Name  approved.**
- **Dial semantics**: bipolar held-state (-1..+1), sampled once per bar;
  reaction lag compensated CLIENT-side at a fixed 2 bars and declared via
  lag_bars (learner-side lag refinement deferred until data shows need).
- **Credit-assignment layering approved**: saliency hypothesizes -> scoped
  sessions train -> ablation replays confirm. Bound: unconfirmed biases cap
  at gentle weight adjustments; ruleset-overlay changes REQUIRE an ablation
  confirmation.
- **First scope: rhythm** (melody waits on gap 19, harmony on gap B).
- **Capture-now approved**: Wend's playground shipped the dial the same day;
  first conformant wont.labeled-run.1 validated end to end (saved to Wend's
  labeled_runs/, server-side).
- **Embed events by default** in labeled runs; regenerate-on-demand for audit.
- **Normalization v1: session-median threshold**; revisit with data.
- Intake brief filed as Tonality PR #160.

## D9 — `scopes` is a SET per session (schema .1 finalized pre-release)

`scope_session: str|None` generalized to `scopes: list[str]` (empty = general).
Rationale: a listening pass legitimately attends to MULTIPLE scopes at once
(Julian, 2026-07-07: "all melodic elements toggled on and all rhythm off"),
and a client parallel-sessions one run — listen with one scope-set, again with
the inverse, ship both (same run_id, different satisfaction + scopes). Kept
schema version `.1` (no released data — Wend's test labels were cleared);
`from_dict` migrates any legacy `scope_session` string into the list, so the
change is forward-safe. Wend ships per-scope toggles + a staging buffer.

## D10 — Wend's scopes are PART-valued (2026-07-07)

Julian: the wont toggles should be per-part, not global pattern-types — "I
may like the harmonic walk or bassline but not the topline, and don't want to
send the wrong feedback." So Wend's `scopes` carry PART names (chords / bass /
topline / drums), dynamically = the parts present in the run. A part-scope
decomposes downstream into that part's pattern atoms (rhythm + note_path), so
this is strictly more informative than pattern-type scoping, and the generic
`scopes: list[str]` field needs no change. Other clients may still use
pattern-type scopes.

## D11 — Validation by controlled recovery experiments, not manual tinkering (2026-07-07)

Julian: don't hand-tinker with wont; run STRUCTURED experiments. Inject
feedback that pushes toward a PREDICTED outcome and measure how the recovered
biases correlate. This is the learner's primary validation method: fabricate
labeled runs with a known synthetic preference (Wend's determinism makes this
cheap — vary one parameter across hundreds of runs, apply a known utility over
it), train, and verify the learner recovers the planted preference before it's
ever trusted on real ears. The recovery harness is the FIRST thing the learner
phase builds. Complements the synthetic-example smoke test already in the
scaffold.

## D12 — Per-part scoping is an optional PRIOR, not the mechanism (2026-07-07)

Julian's own pushback: splitting wont scopes per-part was possibly premature.
The biggest value of the learner is exposing UNKNOWN structure — a working
learner should DECOUPLE which parts matter from the CONSISTENCY of feedback
across many (global) runs, without manual attribution. So: GLOBAL rating (whole
composition, no toggles) is the default and sufficient path; per-part toggles
(D10, kept) are an optional prior that hands the learner a strong hint when the
listener already knows the attribution — an accelerant, not a requirement.
Design implication: the learner must not DEPEND on scope tags; it treats them
as optional side-information.

## D13 — 2026-07-08 — wont gets its own GUI + generator (Julian)

Capture was Wend-side (Wend's playground shipped the dial, D8). Julian now
wants wont to drive its OWN audition harness: generate random/quasi-random runs
sweeping parameters (cadence patterns, melodic walks, chord progressions),
audition each with a satisfaction knob, save labeled runs. Scaffolded:
`wont/generate.py` (ParameterSpace + deterministic quasi/random samplers + the
`Client` seam), `harness/` (serve orchestration + index.html audition skeleton),
`wont/clients/wend.py` (the Wend adapter — STUB, agent wires it). wont stays
client-agnostic: no Wend import in the learner; the client seam is the only
coupling, in `wont/clients/`. Prepared by the Wend agent as handoff scaffolding
(HANDOFF.md); the wont build-agent owns it from here.

## D14 — 2026-07-08 — the scenario: a first-class, reusable training context (Julian)

Julian: set up specific scenarios (e.g. a genre) that start from predefined
Tonality/Wend rulesets and refine to taste, "saving the feedback as specifically
in reference to that scenario for reuse in Wend and other tools." A **Scenario**
(`wont/scenario.py`, schema `wont.scenario.1-draft`) bundles: seed_rulesets
(where a session starts), parameter_space (what the generator sweeps), capture
config (dial range + lag), feedback_dir (scoped store), engine_pins. Every run
captured under a scenario is tagged with `scenario_id` (carried in
`LabeledRun.notes` so the frozen labeled-run schema stays client-agnostic); the
learner trains a scenario-scoped BiasArtifact stamped with the scenario
`fingerprint()`, and Wend requests "the <scenario> bias" and applies it
deterministically for that context. The tag+fingerprint chain is the reuse and
audit handle. Schema is a DRAFT — the build-agent finalizes it (hence the
`-draft` version suffix). Example: `scenarios/lofi-lounge.json`.

## D15 — 2026-07-08 — satisfaction curve is shifted back by the reaction lag (Julian)

Julian: "the satisfaction graph should be shifted back in time by a moment,
since the spikes and valleys will always refer to something which just occurred,
not necessarily what is occurring at that exact moment." This makes the D8
`lag_bars=2` compensation a first-class, always-applied step, not just a stamped
field: `wont/capture.py` shifts every sample EARLIER by the lag (clamped at bar
0, order-preserving → schema-valid) so each label aligns to the music that
CAUSED it; the GUI draws the curve shifted so the user SEES the alignment; the
saved run stamps `lag_bars`. Default stays 2 bars (comparable across sessions).
The learner-side alternative — searching for the lag that best explains a curve
(DESIGN §8.1) — remains a documented hook, deliberately not applied: a fixed,
declared, stamped lag is the honest v1, and the learner can revisit from the
stamp. Covered by tests (compensate_lag / build_curve).
