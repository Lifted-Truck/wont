# LIBRARY — durable, evidence-backed lessons

> Entries follow the template in CLAUDE.md's knowledge-loop block. Candidates
> promote to canonical on a second independent occurrence or human review.
> Refactor like code; don't grow like a log.

<a id="L0001"></a>
[L0001] Tonality venv is the working interpreter | canonical | added: 2026-07-07 |
tags: env-tooling |
lesson: No Python on this Mac has pytest system-wide (checked /usr/bin,
homebrew 3.12/3.13, Framework 3.13). `~/Documents/Tonality/.venv/bin/python`
has pytest 8.4.2 AND `mts` AND importable `Wend` — use it for wont's tests and
any engine-touching script; don't burn time probing interpreters again. |
evidence: setup session — 4 interpreters probed, all ModuleNotFoundError;
Tonality venv ran the suite in <0.2s. Reconfirmed 2026-07-08 (harness build):
the whole 32-test suite + all Wend generation ran only on this venv. |
falsifier: a wont-local venv is created, or pytest appears in a system
interpreter / the Tonality venv is rebuilt without it. |
supersedes: —

<a id="L0002"></a>
[L0002] Wend in-process generation API — the client-seam recipe | candidate | added: 2026-07-08 |
tags: client-seam |
lesson: To generate reproducible music from Wend in-process (the `wont/clients/
wend.py` transport, D16): `oracle = make_oracle("fallback"); rs =
parse_ruleset(text); <set rs.config fields>; rs.config.seed = seed; result =
generate(oracle, rs, initial_key=parse_key(rs.config.key)); parts =
assemble_parts(result, rs.config, oracle, seed)`. Generation knobs are REAL
`Config` dataclass fields — the scaffold's `wend_starter_space` keys
(harmonic_motion, chord_voices, voice_variation, surprise_budget, structure,
surface) all exist; parts are `bass`/`topline`/`drums` bools. Events are
`NoteEvent(start_beat, duration_beats, midi, velocity)` — 4 fields, NO voice;
`assemble_parts` → {chords,bass,topline,drums}. `result.trace.to_json()` →
{seed, ruleset, steps}. Same (ruleset_text, config, seed) → byte-identical
events+trace; no wall-clock in the path. `import Wend` needs the
`synthetic-worlds` parent on sys.path. |
evidence: harness build 2026-07-08 — WendClient wired + `test_harness.py`
determinism test green; 381 notes (chords 80 + bass 64 + topline 55 + drums 182)
scheduled and played in-browser; Explore recon confirmed every signature. |
falsifier: Wend changes its generation entry points (generate / assemble_parts
signatures, Config field names, or the NoteEvent shape), or wont switches to the
subprocess/HTTP transport (D16 swap-in) — then this recipe no longer applies. |
supersedes: —

<a id="L0003"></a>
[L0003] Tonality's Markov/distribution layer (gap 14) IS wont's harmony/Markov surface — consume it | candidate | added: 2026-07-08 |
tags: tonality-channel |
lesson: The "preferences via a Markov bot" direction has a shipped engine
surface — do NOT hand-roll it. `build_transition_matrix(chord_corpus,
state="roman"|"role"|"degree"|"quality", smoothing="laplace")` → row-normalized
first-order transition matrix (versioned prior `distribution.1`, seeded
sample()/walk(), JSON round-trip) IS "a Markov chain over succession tags";
`TransitionMatrix.cross_entropy(held_out)` → bits/transition + perplexity;
`StyleProfile` = ruleset+distributions+provenance bundle. Rulings: (a) never
reimplement transition counting / Laplace / perplexity (engine domain core,
rule 3); (b) the Markov preference signal is a distribution CONTRAST —
`build_transition_matrix(liked)` vs `(disliked)`; the SYMMETRIC contrast
`compare_transition_matrices` (KL + per-transition log-odds, the analogue of
`compare_rulesets`) does NOT exist yet — wont is the named consumer, file a
**brief-2** when the Markov scope materializes; until then `cross_entropy` + the
two matrices cover the asymmetric case; (c) bias-artifact distribution payloads
embed `TransitionMatrix.to_dict()`/`StyleProfile` BY REFERENCE, never a bespoke
wont matrix format; (d) `cross_entropy` is a D11 recovery-harness metric (does
the liked-model give held-out liked material lower perplexity than the
disliked-model?); (e) pin `distribution.1` as a THIRD versioned prior alongside
`key_profile` + `scoring_prior`. Also shipped, bind + drop the interim
workarounds: `ruleset_field_manifest()` (schema `ruleset-fields.2`) — use it
instead of reading `mts.rules.schema.FAMILIES`; `evaluate_ruleset(...,
include_firings=True)` — located firings (the considered-and-held complement to
violations) = the engine-shaped hook for the §7c saliency layer. Division of
labor is unchanged: satisfaction/contrast/thresholding/bias = wont;
transition-math/smoothing/cross-entropy = Tonality. |
evidence: NOTICE `~/Documents/Tonality/integrations/wont/notice-markov-alignment.md`
(2026-07-08), self-verified against both codebases; explicitly no ask/owed now;
durable outcomes tracked in Tonality ROADMAP A10. |
falsifier: the notice is superseded; the `distribution.1` default flips (as
`key_profile` once did); or `compare_transition_matrices` ships — then bind to
it and drop the asymmetric-cross_entropy workaround. |
supersedes: —

<a id="L0004"></a>
[L0004] Per-run pooling: the piece unit is the RUN; scope-separation handles parallel sessions | canonical | added: 2026-07-08 |
tags: stat-soundness |
lesson: When building liked/disliked corpora for `induce_rules` /
`compare_rulesets` / `build_transition_matrix`, pool all of a run's same-label
spans into ONE pseudo-piece per run — `pieces = runs`. Multiple spans from the
SAME run are NOT independent pieces; counting them separately inflates
`induce_ruleset`'s piece-presence support + Fisher independence, the exact
significance-corrupting trap as span duplication (a hard-constraint gotcha), one
level up. The Wend worry — one `run_id` rated in K PARALLEL scoped sessions
(D9/D10, same music, different scope+satisfaction) — DISSOLVES via
scope-separation (response-2): because each scope is mined as its OWN corpus, the
K sessions land in K *different* corpora, so any one corpus sees the run exactly
once → within a corpus, `pieces = runs`. Unit is `(run, scope)`; whole-composition
/ unscoped ratings = one-piece-per-run in the global corpus. Residual needing a
`run_id` grouping-key (clustered/mixed-effects) slice — deferred, wont named —
ONLY for multiple SAME-scope sessions of one run, or a cross-scope joint model.
COROLLARY (train/test): when scoring a distribution with
`TransitionMatrix.cross_entropy(held_out)` — including the D11 recovery metric —
split the held-out set BY RUN, never by span/session, or same-run material leaks
across the split → optimistic perplexity. The run is the unit for partitioning too. |
evidence: response §4 + response-2 (2026-07-08), Tonality agent of record — recipe
answer, no engine work for v1; brief-2 (the K-session question) resolved by
scope-separation. |
falsifier: a cross-scope joint model or a same-scope-repeat need triggers the
clustered slice; or `induce_ruleset`'s piece = input-Sequence semantics change; or
graded sample-weights (gap 20) reframes the piece unit. |
supersedes: —

<a id="L0005"></a>
[L0005] Parallel scoped sessions = attribution + render-efficiency lever, not within-scope power | candidate | added: 2026-07-08 |
tags: credit-assignment |
lesson: Wend's parallel scoped sessions (D9/D10 — one `run_id` rated under
multiple scope-sets) are BOTH a per-part attribution mechanism AND a cross-scope
render-efficiency lever: one audited run feeds K scope corpora at once, so a single
listen harvests bass-signal AND topline-signal (determinism makes the render cheap,
so this efficiency is real). They are NOT within-scope power multiplication —
within any one scope, effective sample size = the distinct runs carrying that scope
(+1 per run, never +K). So the D10 staging buffer earns its complexity for
attribution + efficiency; for significance, lean on more DISTINCT runs per scope.
Squares with D12 (scoped sessions = optional prior / accelerant, not the
mechanism). Practical: don't over-invest in re-auditioning one run many ways to
"get more data" for a scope — audit more distinct runs. |
evidence: response-2 §"the design fork you are gating" (2026-07-08), answering
brief-2 §3. |
falsifier: a cross-scope joint model (the deferred clustered slice) makes K
sessions jointly informative for a single scope's significance. |
supersedes: —
