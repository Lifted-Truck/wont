# INDEX — retrieval map for LIBRARY.md

> Read this in full each session; pull only matching LIBRARY entries into
> context. One line per lesson: `[id] tags — gist`.

## Tag vocabulary (domain-tuned; keep tight)

- `stat-soundness` — statistical-honesty rules for the learner (span
  independence, the no-duplication trap, FDR interactions, pseudo-piece
  granularity)
- `credit-assignment` — findings on disentangling per-scope credit from the
  shared satisfaction signal (ablation / scoped sessions / saliency)
- `labeled-run-schema` — schema + loader gotchas, versioning decisions,
  client-production quirks
- `tonality-channel` — facts from the engine dialogue (gap 19/20 status,
  binding recipes, pinned priors, intake protocol details)
- `artifact-contract` — bias-artifact application/determinism contracts with
  consumer clients (Wend first)
- `client-seam` — wiring a Tonality-client generator INTO wont (transport,
  its generation API, config-key reality, determinism) — the upstream mirror of
  `artifact-contract`
- `env-tooling` — machine/environment facts (interpreters, venvs, repos,
  branches)

## Entries

- [L0001] env-tooling — no system pytest on this Mac; use the Tonality venv
  interpreter (pytest + mts + importable Wend) for all wont test/analysis runs.
- [L0002] client-seam — Wend in-process generation recipe: make_oracle →
  parse_ruleset → set rs.config → generate → assemble_parts; Config keys are
  real, NoteEvent is 4 fields, deterministic; `import Wend` needs the parent dir.
- [L0003] tonality-channel — Tonality's gap-14 Markov/distribution layer is
  wont's harmony surface: consume `build_transition_matrix`/`cross_entropy`,
  don't reimplement; `compare_transition_matrices` is the named-consumer gap
  (file brief-2); pin `distribution.1`; firings + field-manifest also shipped.
- [L0004] stat-soundness — piece unit = the RUN (`pieces = runs`); parallel
  scoped sessions of one run_id dissolve via scope-separation (K sessions → K
  corpora, run seen once each); split cross_entropy held-out by run too. RESOLVED.
- [L0005] credit-assignment — parallel scoped sessions are an attribution +
  cross-scope render-efficiency lever, NOT within-scope power; a scope's N =
  distinct runs carrying it, so audit more distinct runs for significance.
