# wont — design document

> Status: **draft for dialogue** (2026-07-07). Nothing below is built except
> §4 (the labeled-run schema, which is code). Everything else waits on the
> Tonality intake response (branch `wont-intake-brief`) and Julian's review.
> Where this document records an open question, that is deliberate — asking
> beats guessing.

## 1. Purpose

A user turns a satisfaction dial while a generated composition plays. The
time-stamped signal becomes labeled training data for classical ML that
learns which rulesets/parameterizations correlate with satisfaction and
biases future generation. Modular: usable by any Tonality client.

Hard constraints, inherited and non-negotiable:

- **AI/deterministic boundary.** Training runs offline. The learner emits
  versioned, provenance-stamped artifacts; a consumer applies a pinned
  artifact deterministically; pinned artifact + seed reproduces exactly.
  Nothing learns online inside a generator or engine.
- **Feature vocabulary is Tonality's** (response-3, recorded): melodic/
  rhythmic atoms, rule firings, conformance reports, succession tags. No
  bespoke music features. Tonality owns vocabulary + deterministic feature
  extraction; wont owns the ML.
- **Classical ML only**: Markov chains, bandits, logistic-class models.
  Interpretable weights are a feature, not a compromise — the readout must
  stay human/agent-auditable.
- **Statistical honesty.** Response-3 R2.1 is binding: liked and disliked
  spans are mined as *separate corpora* and the induced rulesets are
  *contrasted* — the contrast IS the preference signal. Never duplicate
  spans to fake sample weights (it corrupts the Fisher/BH-FDR significance
  model). Graded sample-weights are Tonality gap 20, contingent on binary
  proving too coarse.

## 2. Position in the ecosystem

```
 client (Wend, ...)                     wont                        Tonality (mts)
 ─────────────────                      ────                        ──────────────
 generates + plays          ┌──►  ingests LabeledRuns         owns the vocabulary:
 captures dial → curve      │     slices spans by threshold   analyze_melody/rhythm,
 emits LabeledRun ──────────┘     builds per-scope corpora ──► induce_rules,
                                  contrasts rulesets ◄──────── compare_rulesets,
 applies BiasArtifact  ◄───────── emits (1) BiasArtifact       tag_transition,
 deterministically                      (2) Readout            evaluate_ruleset
                                            │
                                            └──► humans/agents run independent
                                                 analysis with engine tools
```

Three parties, three responsibilities:

| party | owns | must not do |
|---|---|---|
| client | signal capture, run fingerprinting, deterministic artifact application | learn online; invent features |
| wont | span slicing, corpus construction, the ML, artifact + readout emission | reimplement engine analysis; bespoke vocabulary |
| Tonality | atoms, induction, significance model, ruleset DSL, comparison | hold the satisfaction signal or the learned weights |

**Boundary module:** `wont/engine.py` (not yet written) will be the ONLY file
importing `mts` — Python-import door, offline latency budget, numeric
canonical data; display/spelling never enters the learner. Engine priors used
in any extraction are pinned and stamped into every artifact and readout.

## 3. Pattern scopes

A **scope** is an independently targetable, independently trainable slice of
the musical surface, with its own feature vocabulary (drawn from Tonality
atoms), its own corpus construction, and its own bias artifact. One shared
satisfaction signal feeds all scopes; disentangling credit is §7.

### 3.1 `note_path` — melodic contour & tendency

What the melody *does* note-to-note.

Vocabulary (all shipped, `analyze_melody` + NHT typing):
- approach/departure intervals with step/skip/leap classes
- Parsons contour (u/d/r), ambitus
- NHT types against caller-provided harmony spans: passing, neighbor,
  appoggiatura, escape, suspension, anticipation, pedal
- arrival treatment (step-approached vs leap-approached — the exact measure
  Wend used in brief-3 R1: 65% → 26%)
- when gap 19 ships: melodic tendency / scale-degree stability as a cited
  prior, replacing hand notions of "stable landing"

Ruleset induction: `induce_rules` over the melody atom fields is shipped —
this scope can run the full contrast recipe today.

### 3.2 `rhythm` — syncopation & metric placement

Where onsets sit against the felt beat.

Vocabulary (all shipped, `analyze_rhythm` + `analyze_swing` +
`extract_groove`):
- metric placement classes: downbeat / beat / offbeat / subdivision
- the precise syncopation predicate (weak onset sounding through the next
  stronger grid line)
- durations + inter-onset intervals
- swing feel (straight/swung/reversed/mixed, division-fraction evidence) —
  versioned prior `swing-feel.1`
- groove templates as a feel fingerprint (per-slot offset + accent)

Ruleset induction over rhythm atoms is shipped — full contrast recipe
available today.

### 3.3 `harmony` — chord-progression patterns

How chords succeed one another.

Vocabulary (shipped): `tag_transition` succession tags — functional
(`dominant_resolution`, `descending_fifth`, `prolongation`, `retrogression`,
`applied_dominant`, `borrowed`, cadential formulas), voice-leading
(`smooth`, `parsimonious` + P/L/R, common-tone count, `chromatic_mediant`),
raw axes (`vl_distance`, `common_tones`, `root_interval`, `color_shift`);
`cadences` for formula events; key regions / `structural_keys` for context.

**Known gap:** progression-level *ruleset* vocabulary (rules over chord
successions) is Tonality Phase 4.6 "gap B" — Wend is its first named
consumer; wont registers as the second (intake brief §3). Until it ships,
the harmony scope's v1 is a **succession-tag frequency contrast** (tag
contingency tables between liked/disliked corpora) rather than
`induce_rules` — visibly-minimal, documented as the swap-in point per the
shared-engine protocol (rule 5).

**Distribution surface (gap 14, shipped — the Markov direction).** Tonality's
Markov/distribution layer gives this scope its second, richer engine surface
(Markov-alignment notice, 2026-07-08; D18): `build_transition_matrix(chord_corpus,
state="roman"|"role"|"degree"|"quality", smoothing="laplace")` IS "a Markov chain
over succession tags" (versioned prior `distribution.1`), and the Markov
preference signal is the distribution *contrast* `build_transition_matrix(liked)`
vs `(disliked)` — the exact analogue of the `induce_rules → compare_rulesets`
pipeline. wont consumes this; it never hand-rolls transition counting, Laplace
smoothing, or perplexity (rule 3). The *symmetric* contrast
`compare_transition_matrices` (KL + per-transition log-odds) is the one genuine
gap — wont is the **named consumer**; file a brief-2 when this scope materializes.
Until then, `TransitionMatrix.cross_entropy(held_out)` (bits/transition +
perplexity) covers the asymmetric case and doubles as a D11 recovery-harness
metric. **Stamp (response-2):** when scoring with `cross_entropy`, split the
held-out set **by run**, never by span or session — same-run material on both
sides of the split leaks (identical underlying music) and returns optimistic
perplexity; the run is the unit for train/test partitioning as well as for
piece support.

### 3.4 Extensibility

A scope is a registered triple: `(scope_id, extractor, corpus_builder)` over
engine vocabulary. Candidates already visible: `voicing` (spread/inversion/
drop-N via voicing analysis), `feel` (groove-template distance), `key_journey`
(modulation relations via structural_keys). None in v1.

## 4. The labeled run (schema — this part is code)

The unit of training data. Designed so **any Tonality client can produce
one**: nothing in the required core is Wend-specific.

`wont/schema.py`, `SCHEMA_VERSION = "wont.labeled-run.1"`:

```
LabeledRun
  schema_version   "wont.labeled-run.1"
  run_id           sha256 over canonical (client, ruleset_text, config, seed)
                   — derived, verified on load; the reproducibility identity
  client           {name, version}          e.g. {"wend", "0.9"}
  engine_pins      {prior_name: version}    e.g. {"key_profile": "kk-1982.1"}
  ruleset_text     verbatim generation ruleset (client's own DSL — opaque)
  config           JSON object (client's full parameterization)
  seed             int — with ruleset_text + config, regenerates the run
                   bit-identically on the client
  trace            client-opaque JSON (Wend: Trace.to_json()); the learner
                   only requires bar alignment to exist in the curve
  satisfaction     SatisfactionCurve:
                     samples      [(bar, value), ...] bars non-decreasing
                     value_min/max declared range (client's dial units)
                     lag_bars     optional reaction-lag compensation already
                                  applied by the client (0 if none)
  scopes           list of scope_ids this session attends to (empty = general);
                   SCOPED LISTENING SESSION (credit assignment, §7b)
  events           optional {part_name: [[onset_beats, dur_beats, midi,
                   velocity, voice], ...]} — Tonality Event-shaped, so the
                   learner can analyze without regenerating (open question 8.2)
  notes            free-form list
```

Validation is **total** (every error reported, `validate_ruleset` style).
JSON round-trip is byte-stable modulo key order. Loader: single run or a
corpus directory.

Deliberately NOT in the schema: satisfaction thresholds (a learner-side
policy, not a data property), any Tonality analysis (derived, not captured),
wall-clock timestamps in the core (provenance may carry a capture date as
metadata; nothing computes from it).

## 5. Bias artifacts (schema — design only, not yet code)

`SCHEMA_VERSION = "wont.bias-artifact.1"` (to be frozen after dialogue):

```
BiasArtifact
  schema_version   "wont.bias-artifact.1"
  artifact_id      content hash of payload + provenance
  scope            "note_path" | "rhythm" | "harmony" | ...
  method           e.g. "contrast-induction.1" — versioned learner recipe
  provenance
    training_runs  [run_id, ...] with per-run content hashes
    threshold      the like/dislike split used (value + hysteresis)
    engine         {mts_version, pinned priors, induce_rules scoring_prior}
    learner        wont version
    exploratory    bool — propagated from induce_rules' <~30-piece flag
  payload          method-specific; for contrast-induction.1:
    liked_ruleset     validated Tonality DSL JSON (induced from liked corpus)
    disliked_ruleset  validated Tonality DSL JSON
    contrast          compare_rulesets output: unique-to-liked (prefer),
                      unique-to-disliked (avoid), shared, conflicts —
                      each rule with evidence (support/confidence/leverage/p/q)
    bias_weights      {rule_id: weight} — the collapsed, consumer-facing form
  application      contract note: consumers apply deterministically
                   (conformance-gated candidate selection, or compiled into
                   policy parameters); artifact + seed reproduces exactly
```

Key property: the payload's rulesets ARE Tonality DSL artifacts —
`validate_ruleset`-clean, so the artifact doubles as engine-analyzable data.
Consumers never see raw training data through the artifact; the plural
evidence (per-rule margins, p/q) rides along per the consume-plural-outputs
rule — a client may re-rank rather than take `bias_weights` as gospel.

**Distribution payloads travel by reference, as Tonality types** (D18, extending
the response §5 discipline to the Markov half): a `BiasArtifact` carrying a Markov
payload embeds `TransitionMatrix.to_dict()` (or a whole `StyleProfile`) verbatim,
never a bespoke wont matrix format. The `BiasArtifact` container stays wont-schema
— it wraps the *satisfaction-derived contrast*, which is ours — but its
distribution content is Tonality's type, by reference. Provenance then pins a
THIRD versioned prior, the smoothing prior `distribution.1`, alongside
`key_profile` and the induction `scoring_prior`. This keeps the "mts + the readout
reproduces the numbers exactly" acceptance bar intact.

## 6. The readout (dual output #2)

The independent-analysis export — everything an agent needs to check our
work with engine tools, no wont code required:

```
readout/
  manifest.json          SCHEMA_VERSION, provenance (same block as artifact),
                         file inventory + hashes
  corpora/
    <scope>/liked/       pseudo-piece JSONs (Tonality Sequence-shaped)
    <scope>/disliked/
  rulesets/
    <scope>.liked.json      induced ruleset, DSL JSON, validated
    <scope>.disliked.json
    <scope>.contrast.json   compare_rulesets output
  records/
    <run_id>.dataset.json   DatasetRecord-style per-span annotations
                            (SCHEMA_VERSION "1.0" from mts/dataset/record.py)
                            + satisfaction label per span
```

Design test: a fresh agent with only `mts` and this directory can re-run
`induce_rules` on the corpora, `compare_rulesets` on the rulesets, and
`evaluate_ruleset` of either ruleset against any span — and reproduce our
numbers exactly (deterministic engine + pinned priors + committed corpora).

**This readout is the committed, versioned tier of the capture-data policy (D19).**
Raw captures are gitignored working data (tier 1); the readout is the *sealed
corpus* committed alongside a released artifact (tier 2), and its `manifest.json`
(file inventory + hashes) is the always-committed index (tier 3) that makes an
artifact's `training_runs` (§5) verifiable by hash. Writing the readout IS the
promotion step; it lands under `corpora/<scenario>/<seal-date>/`. Gated with the
learner — design-only until then.

## 7. Credit assignment across scopes — THE open question

One dial, three scopes: when satisfaction rises, which scope earned it?
Three candidate mechanisms, to be developed in dialogue — likely a layered
combination, not a single winner.

### (a) Ablation replays — the controlled-experiment primitive

Wend regenerates any run bit-identically with one scope's settings varied
(shipped as playground "variation replay"). Rate original and variant; the
satisfaction delta is *causally* attributable to the varied scope.

- **For:** the only mechanism with a causal claim; determinism makes the
  counterfactual exact; Wend already surfaces it.
- **Against:** costs human listening time linearly per ablation (the scarcest
  resource in the loop); combinatorial across scopes and settings;
  **interaction effects** — varying the rhythm scope changes how the melody
  *reads*, so single-scope deltas aren't perfectly clean; requires client
  support for scope-isolated variation (Wend has it; a portable client
  contract for "vary only scope X" needs defining).
- **Role:** the *confirmatory* instrument — spend listening time verifying
  candidate findings from (c), not exploring blind.

### (b) Scoped listening sessions — cheap targeted labels

A run auditioned explicitly to rate one scope ("turn the dial for the
melody only"). The `scopes` LIST field carries it — a pass may target a SET
(e.g. all melodic scopes on, rhythm off), and a client may PARALLEL-SESSION
one run: listen with one scope-set, again with the inverse, ship both
(same run_id, different satisfaction + scopes). Wend implements exactly this with per-PART toggles + a staging buffer:
its `scopes` are PART names (chords/bass/topline/drums), because a
listener rates what they hear as a unit — "I like the bass, not the
topline." A part-scope decomposes downstream into that part's pattern
atoms (a part carries both rhythm and note-path aspects), so per-part is
STRICTLY more informative than per-pattern-type, not a different axis.
The generic `scopes: list[str]` field holds either vocabulary.

- **For:** direct per-scope labels at ordinary session cost; honest about
  intent; trivial to implement (a UI toggle + one schema field).
- **Against:** attention is not a filter — raters cannot fully mute other
  scopes (halo effects: a great groove flatters the melody rating);
  multiplies session count if full per-scope coverage is wanted; labels are
  intent-scoped, not causally scoped.
- **Role:** the *primary experimental* layer for v1 — cheap enough to run
  routinely, honest enough to train per-scope artifacts with a documented
  caveat.

### (c) Per-scope feature saliency — observational, free

From ordinary (unscoped) sessions: extract per-scope features per span,
correlate each scope's features with the satisfaction label independently
(per-scope contrast mining as in §9; optionally per-scope logistic weights).

- **For:** uses every labeled run ever captured, zero extra listening;
  the v1 contrast recipe already IS this per scope.
- **Against:** purely correlational — scopes co-vary within a run (one
  config generates all parts), so confounding is structural, not incidental;
  the multiple-comparisons risk across scopes mirrors the FDR concern inside
  each scope; a scope can absorb credit for a co-varying neighbor.
- **Role:** the *always-on baseline* — generates hypotheses; never trusted
  alone for artifact emission without (a)- or (b)-grade support. Artifacts
  trained purely on (c) carry an `exploratory`-style honesty flag.

**Proposed layering (for dialogue):** (c) continuously → hypotheses; (b)
routinely → per-scope training labels; (a) sparingly → confirmation of any
finding that will bias generation by more than a bounded amount. The bound
itself is an open design knob.

A statistical wrinkle, **resolved** (response §4 + response-2, 2026-07-08; D18).
The engine's honesty ruling: spans cut from the SAME run are not independent
pieces, so pool a run's same-label spans into ONE pseudo-piece — `pieces = runs`,
never separate per-span pieces (that inflates `induce_rules`' piece-presence
support + Fisher independence, the span-duplication trap one level up).

Binding this to Wend surfaced — and Tonality resolved — the level above: Wend
parallel-sessions a single `run_id` (D9/D10: same music rated under multiple
scope-sets, different satisfaction each). The independence unit is **`(run,
scope)`**, and because **each scope is mined as its own corpus** (§3), within any
one corpus it reduces to `pieces = runs` — the K parallel sessions land in K
*different* corpora, so no corpus ever sees the run twice and the pseudo-replication
never arises (response-2). A `bass`-scoped session of run R feeds R's bass atoms to
the bass corpus; a `topline` session of the same R feeds the topline corpus;
whole-composition / unscoped ratings stay one-piece-per-run in the global corpus.
The only residual is **multiple same-scope sessions of one run** (pool if
same-label) or a **cross-scope joint model** — the sole cases needing a `run_id`
grouping-key (clustered / mixed-effects) slice, recorded as contingent engine work
with wont named, and deferred (don't build; return with the trigger).

**Design consequence (the fork this gated).** Parallel scoped sessions are an
*attribution* lever and a *cross-scope render-efficiency* lever (one audited run
feeds K scope corpora at once — harvest bass-signal *and* topline-signal from one
listen; determinism helps here), but **not** within-scope power: a scope's
effective N is the distinct runs carrying it (+1 per run, never +K). So the D10
staging buffer earns its complexity for attribution + efficiency; for significance,
lean on more *distinct* runs per scope and treat scoped sessions as the D12
optional-prior accelerant, not a multiplier. (Synthetic D11 recovery is unaffected:
fabricated labels, one per run.)

## 8. Open questions (beyond credit assignment)

1. **Reaction lag.** A human turns the dial 1–2 bars after the thing they
   liked. Client-side compensation (`lag_bars`), learner-side shift search,
   or both? Wrong lag mislabels boundary bars — plausibly the biggest noise
   source in the whole loop.
2. **Embed events or regenerate?** `events` is optional in the schema.
   Embedding makes runs analyzable engine-side without the client installed
   (portable, larger files); regeneration keeps runs small but couples the
   learner to every client's presence and version. Current lean: embed for
   interchange, regenerate for audit.
3. **Span slicing policy.** Threshold with hysteresis (dial jitter), minimum
   span length in bars, cut at bar vs phrase boundaries — all learner-side
   policy; needs Tonality's guidance on pseudo-piece granularity (intake §4).
4. **Value normalization across users/sessions.** Dial habits differ
   (per-session z-scoring vs declared absolute range). v1: within-session
   threshold at the session median — revisit with data.
5. **Artifact application contract.** Conformance-gated candidate selection
   vs compiling weights into policy parameters — Wend Phase G leans toward
   the former; the artifact schema stays agnostic (it ships rulesets +
   weights; the client chooses the mechanism and records it).

## 9. v1 plan — the threshold + contrast recipe (response-3, binding)

Smallest honest loop, everything on shipped engine surface:

1. **Capture** (client): Wend playground records the dial → emits
   `LabeledRun`s (schema is done; Wend E.2 signal-capture is Wend-side work).
2. **Slice** (wont): threshold each run's curve at the session median with
   hysteresis → liked spans / disliked spans; drop spans shorter than the
   minimum; **never duplicate**.
3. **Build corpora** (wont, per scope): each **run** becomes a pseudo-piece in
   the scope's vocabulary (pool that run's same-label spans — `pieces = runs`,
   §7, response §4/response-2; never one-per-span) — melody events for
   `note_path`, onsets for `rhythm`, chord successions for `harmony`. Each scope
   is its own corpus, so a run scoped to that scope contributes exactly once.
4. **Mine separately** (engine): `induce_rules` on liked and disliked corpora
   per scope (`note_path`, `rhythm`); succession-tag frequency contrast for
   `harmony` until Phase 4.6 gap B.
5. **Contrast** (engine): `compare_rulesets` liked-vs-disliked → unique /
   shared / conflicting rules with evidence. The contrast is the preference
   signal.
6. **Emit** (wont): per-scope `BiasArtifact` + the readout directory.
   Propagate `exploratory` flags honestly; below-floor corpora emit a
   readout but NO artifact (no biasing generation on flagged evidence).
7. **Apply** (client): deterministically, pinned, seeded.
8. **Close the loop**: variation replay (a) on the top contrast finding —
   the first confirmatory experiment.

Deferred, with triggers: graded sample-weights (gap 20 — trigger: binary
split demonstrably too coarse on real curves); bandit over parameterizations
(trigger: enough sessions that exploration policy matters); per-scope
logistic saliency (trigger: corpora large enough to split; engine hook now
shipped — `evaluate_ruleset(..., include_firings=True)` located firings, D18);
Markov chains over succession tags (trigger: harmony scope goes Markov —
consume `build_transition_matrix` + contrast; file a brief-2 for the symmetric
`compare_transition_matrices` slice, wont named consumer, D18).
