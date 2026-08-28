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

## D16 — 2026-07-08 — Wend client transport is IN-PROCESS import (build agent)

The HANDOFF left the Wend seam's transport to the build agent (in-process import
vs subprocess/HTTP). Chose **in-process** (`wont/clients/wend.py` is the one
Wend-importing module): `make_oracle → parse_ruleset → set rs.config →
generate() → assemble_parts()`. Rationale: Wend is a sibling package in the same
`synthetic-worlds/` monorepo and wont runs on the Tonality venv, which imports
Wend cleanly; in-process hands back the in-memory `result.events` /
`assemble_parts` structures directly — no MIDI round-trip, no fidelity loss,
determinism airtight (same ruleset_text+config+seed → byte-identical events +
trace, verified in tests). The global shared-engine protocol's "data contract,
not a network boundary" (rule 1) is satisfied by the GeneratedRun boundary, not
by a socket. Subprocess (`python -m Wend`) and HTTP (`/generate`, port 8770 —
Wend does expose it) remain a documented swap-in for the day wont must run
without Wend's Python present; the seam's normalized `GeneratedRun` return makes
that swap invisible downstream. NOTE: this is wont↔Wend (two Tonality
consumers), NOT the Tonality engine boundary — `wont/engine.py` (the sole `mts`
importer) is still unwritten and belongs to the learner phase.

## D17 — 2026-07-08 — scenario schema frozen to `wont.scenario.1`; audition harness built

The audition harness (D13) is built and green end-to-end: `harness/serve.py` (a
stdlib-`http.server` adapter over the pure helpers — `/scenarios`, `/sweep`,
`/save`, port 8771), `harness/index.html` (scenario picker → sweep → WebAudio
playback of the returned per-part events → per-bar dial capture → lag-shifted
graph → save), and the live `WendClient` (D16). Building it exercised every
`Scenario` field, so the draft schema is **finalized**: `wont.scenario.1-draft`
→ `wont.scenario.1` (no shape change; the fingerprint excludes `schema_version`,
so runs already tagged with a scenario fingerprint are undisturbed). Scaffold
fixes made along the way: `serve.SCENARIO_DIR` used two `..` but `scenarios/` is
one level up from `harness/` (empty scenario list); `WendClient.generate_run`
was a stub. New tests: `tests/test_harness.py` (client determinism, effective-
config coercion, sweep distinctness, full capture→save→reload round-trip over
real music); `conftest.py` puts the `synthetic-worlds` parent on `sys.path` so
`import Wend` resolves in the suite (Wend-dependent tests skip if it is absent).
The **learner remains unbuilt and gated** (HANDOFF / DESIGN §5–§9) — the harness
is capture/audition tooling, the D11 synthetic-recovery harness is its first
step and is deliberately NOT started here.

## D18 — 2026-07-08 — bind to Tonality's Markov-alignment notice (gap 14 + housekeeping)

Received `~/Documents/Tonality/integrations/wont/notice-markov-alignment.md`
(2026-07-08) — a proactive alignment pass from the Tonality dev loop, "no ask,"
recording the shared vocabulary for wont's "preferences via a Markov bot"
direction now that Tonality shipped its distribution layer (gap 14) after the
founding response. Nothing owed now (learner is design-only, gated); this logs
the bindings adopted into the design of record so the future learner-build
session inherits an aligned contract. Full bindings captured in LIBRARY [L0003]
(tonality-channel) + [L0004] (stat-soundness). Adopted:
- **Consume the gap-14 layer, don't reimplement.** `build_transition_matrix(...,
  state="roman"/"role"/..., smoothing="laplace")` is "a Markov chain over
  succession tags"; `cross_entropy` gives perplexity; `StyleProfile` bundles
  ruleset+distributions. Transition math/smoothing/perplexity are engine domain
  core (rule 3) — wont keeps satisfaction/contrast/thresholding/bias only.
- **The symmetric distribution contrast is the one real gap.**
  `compare_transition_matrices` (KL + per-transition log-odds — the Markov
  analogue of `compare_rulesets`) does NOT exist yet; wont is the **named
  consumer**. Posture identical to graded-weights (gap 20) + firing-locations:
  don't build speculatively — **file a brief-2** when the Markov/harmony scope
  materializes. Until then, `cross_entropy` + the two matrices cover the
  asymmetric case.
- **Distribution payloads travel by reference as Tonality types** (D-consistent
  with response §5): a Markov `BiasArtifact` embeds `TransitionMatrix.to_dict()`
  / `StyleProfile` verbatim, never a bespoke wont matrix format.
- **Pin `distribution.1`** as a third versioned prior alongside `key_profile`
  (client) + `scoring_prior` (induction) on any artifact carrying a distribution.
- **Two response loose ends shipped — bind, drop workarounds:**
  `ruleset_field_manifest()` (schema `ruleset-fields.2`) replaces reading
  `mts.rules.schema.FAMILIES`; `evaluate_ruleset(..., include_firings=True)`
  yields located firings — the engine-shaped hook for the §7c saliency layer.
- **Resolves an open question in our own design (§7):** the "spans from one run
  aren't independent pieces" wrinkle is answered — `pieces = runs` (per-run
  pooling), never per-span. Folded into DESIGN §3.3 / §5 / §7 / §9 with this
  notice attributed. This narrows corpus construction (one pseudo-piece per run
  per label), which touches the credit-assignment design (D9–D12).
  — **UPDATE (Julian, same day): reopened.** The ENGINE ruling (spans aren't
  independent pieces) stands, but its interaction with Wend's per-run capture is
  NOT cleanly closed: Wend runs are long/multi-span AND Wend parallel-sessions one
  `run_id` (D9/D10 — same music, different scope-set + satisfaction). `pieces =
  runs` then either pools those parallel sessions into one piece (collapsing the
  scoped signal D10 was built for) or admits correlated same-music pieces (the
  trap). This **warrants a dialogue** — primary question to Tonality (brief-2):
  are parallel same-run sessions one piece or correlated pieces, and can
  `induce_rules` model the within-run/across-session correlation rather than
  exclude it? With a Wend-capture design thread (does D10's parallel-session
  multiplication still earn its keep if power is bounded by audited runs, not
  spans?). DESIGN §7 + [L0004] demoted from "resolved" to "open, under dialogue."
  Do NOT treat `pieces = runs` as settled for Wend.
  — **brief-2 DRAFTED** (Julian's call, 2026-07-08):
  `~/Documents/Tonality/integrations/wont/brief-2.md` — the K-parallel-scoped-
  sessions-per-run_id question (Q1 independence unit; Q2 clustered/mixed-effects
  slice, wont named consumer; Q3 per-(run,scope) unit; Q4 same for the gap-14
  distribution layer). Written into the channel but **unstaged / not filed** —
  left for Julian's review + commit/push, per the D5 no-push precedent.
  — **RESOLVED (response-2, 2026-07-08):** recipe answer, no engine work for v1.
  The K-session problem DISSOLVES via scope-separation: each scope is its own
  corpus, so K parallel scoped sessions of one `run_id` land in K *different*
  corpora → within a corpus, `pieces = runs`; the unit is `(run, scope)`.
  Whole-composition / unscoped ratings stay one-piece-per-run in the global corpus.
  The clustered/mixed-effects (`run_id` grouping-key) slice is needed ONLY for
  multiple SAME-scope sessions of one run or a cross-scope joint model — contingent
  engine work, wont named, deferred. New stamp: split `cross_entropy` held-out sets
  BY RUN (never span/session) or perplexity leaks optimistic. Design fork settled:
  parallel scoped sessions are an attribution + cross-scope render-efficiency lever,
  NOT within-scope power (a scope's N = distinct runs carrying it; lean on more
  distinct runs). Folded into DESIGN §3.3 / §7 / §9-step-3; [L0004] promoted to
  canonical, [L0005] added. Durable outcomes in Tonality ROADMAP A10.

## D19 — 2026-07-09 — capture-data versioning: a three-tier promotion model (Julian)

Whether captured LabeledRuns are versioned or gitignored (raised after the
harness build). Chosen: a PROMOTION MODEL, not a binary — because a capture is
two kinds of data. The satisfaction curve + scopes are **primary and
irreplaceable** (frozen human listening time — the loop's scarcest resource, §7);
ruleset_text / config / seed / trace / events are **derived** (reproducible from
the client on pinned versions, D4/D16). The tiers:

1. **Working / synthetic captures → gitignored** (current default,
   `scenarios/*/runs/`). Dev auditions and the D11 synthetic-recovery runs
   (hundreds of fabricated labels per experiment) are throwaway, high-volume,
   reproducible — they never enter git. BUT gitignored ≠ disposable: the working
   dir holds PRIMARY human labels, so it must live under a backed-up / synced
   path (one `rm -rf` from gone otherwise). Standing recommendation to Julian;
   not repo-enforced.
2. **Sealed corpus → committed.** The finite, curated set of runs that trained a
   RELEASED bias artifact is committed with the artifact, under a non-ignored
   path (`corpora/<scenario>/<seal-date>/`). This is what makes the artifact's
   `training_runs` provenance (§5) reproducible — the doctrine's "reproduce
   exactly" is hollow if the training inputs live only on one machine. The
   readout writer (§6) IS this promotion mechanism; it is learner-phase and
   gated, so tier 2 is design-only until then.
3. **Always-committed manifest.** A tiny index (run_id + content-hash +
   capture-date + scenario_fp per run) is committed even while bulky payloads
   stay in tier 1's ignored store — it diffs cleanly, records WHAT exists, and
   lets any artifact's training set be verified by hash without the payloads in
   git. The readout's `manifest.json` (file inventory + hashes, §6) fills this
   role for a sealed corpus.

Rationale beyond primary-vs-derived: (a) **git is a bad database** — JSON data
diffs are noise, blobs bloat clones; reserve it for curated/sealed sets + the
tiny manifest, not raw high-volume captures. (b) **Client drift** — "regenerate
on demand" degrades as Wend evolves, so a sealed corpus keeps its embedded
events (D8) as the record of what was actually heard. (c) **The asymmetry** —
gitignore-now is reversible (`git add` later); commit-everything-now is not
(blobs stay in history forever). Start conservative, promote deliberately.

Implication: **no code now** (readout writer gated). The harness already saves
into tier 1 (gitignored). When the learner/readout lands, sealing a corpus =
running the readout writer into `corpora/<scenario>/<seal-date>/` and committing
it + the manifest. `.gitignore` + this decision are the durable record until then.

## D20 — 2026-08-28 — the oracle exists; Phase-2 gate lifted (Julian, session close)

Two things, both from the session close.

**(a) `./verify` now exists.** The repo carried a vendored, checksummed `.kit/`
(kit 2.5.0) but no project-owned `./verify` to source it — so every gate it
ships (leak, kit-integrity) was inert, and `state.py` reported "no recorded
run". Written now, in the fleet's dispatcher shape: Layer-0 `fast` =
kit_integrity + leak_gate + plant_not_tracked + interpreter_gate +
schema_frozen_gate + test_gate; Layer-E `full` adds determinism_gate (one
(ruleset_text, config, seed) must regenerate byte-identical music — D4/D16, the
invariant every reproducibility claim rests on). Both **green** at close.
`schema_frozen_gate` makes the CLAUDE.md "versions are frozen" rule an oracle
rather than a convention. The interpreter is `$WONT_PYTHON`, defaulting to a
`$HOME`-relative Tonality venv path — never a machine-absolute literal, which is
what the leak gate exists to stop. Also added: `ROADMAP.md` (the phase-gated
sequence + the gate, now the "what's next" authority, pointed to from CLAUDE.md
and README), `.harness/` ignored (kit v2), and a README de-drift — it still
announced "Harness-scaffold phase" with the client/server/UI as unbuilt stubs,
which the D13–D17 work had made false.

**(b) The Phase-2 gate is LIFTED.** ROADMAP's learner gate required both the
Tonality intake dialogue resolved (done: brief/response, brief-2/response-2, the
notices) and Julian's approval. At close, asked for the first move next session,
Julian chose **"Start Phase 2 (`wont/engine.py`)"** — that is the approval, on
the record. Next session opens the `mts` boundary module, then slicer → per-
`(run, scope)` corpus builder → the D11 synthetic-recovery experiment, gated by
the pre-registered Layer-0 recovery criterion. The §8 policy knobs (threshold +
hysteresis, min-span, normalization) are decided AT that build, explicitly, not
inherited from whatever the first implementation happens to do.
