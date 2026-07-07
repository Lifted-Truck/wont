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
