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
