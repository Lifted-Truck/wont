# wont — agent notes

Preference-learning system for Tonality-based generators. **Name is
provisional** (see README).

**Built:** the audition harness (D13/D16/D17) — generate/sweep runs, audition
with the satisfaction dial, save scenario-tagged labeled runs. Run it (Tonality
venv, from this dir): `~/Documents/Tonality/.venv/bin/python -m harness.serve`
→ http://127.0.0.1:8771. The one Wend-importing module is `wont/clients/wend.py`
(in-process transport). **Not built / gated:** the LEARNER (DESIGN §5–§9) and
`wont/engine.py` (the sole `mts` importer) — do NOT build them until the
Tonality intake dialogue (branch `wont-intake-brief`) resolves and Julian
approves; per D11 the learner's FIRST build is the synthetic-recovery harness.

## Pointers

- [ROADMAP.md](ROADMAP.md) — phase-gated sequence + the learner gate. Start
  here for "what's next"; it owns the *what/when* (DESIGN owns the *how*).
- [DESIGN.md](DESIGN.md) — the design of record (scopes, schemas, credit
  assignment, v1 plan). Outranks anything else here on design detail.
- [DECISIONS.md](DECISIONS.md) — append-only decision log.
- `~/Documents/Tonality/INTEGRATION.md` — engine capability schematic.
- `~/Documents/Tonality/integrations/wend/brief-3.md` + `response-3.md` — the
  founding dialogue. Response-3's recipes are **binding**: mine liked vs
  disliked spans as SEPARATE corpora and contrast the induced rulesets;
  weighted conformance derives client-side from beat-tagged violations.
- `~/Documents/Claude/synthetic-worlds/Wend/ROADMAP.md` Phase E.2 — the
  first client's agreed architecture.

## Gotchas (hard constraints)

- **NEVER duplicate spans to fake sample weights** — it corrupts
  `induce_rules`' Fisher/BH-FDR significance model (response-3 R2.1).
  Graded sample-weights are Tonality gap 20, contingent; we are the named
  consumer if binary liked/disliked proves too coarse.
- **AI/deterministic boundary**: training is offline; artifacts are
  versioned + provenance-stamped; a pinned artifact + seed reproduces
  exactly. Nothing learns online inside a generator.
- **Feature vocabulary is Tonality's** — atoms, rule firings, succession
  tags. No bespoke music features. Classical ML only (Markov/bandit/
  logistic) — no deep nets, ever.
- **One boundary module** (`wont/engine.py`, not yet written) is the only
  file that may `import mts`. Everything downstream consumes normalized data.
- **Pin engine priors** in every artifact and readout (e.g. key profile
  `kk-1982.1` vs `tkp-cbms.1` — the upstream default flip changed margin
  scales; Wend pins kk-1982.1).
- Schema versions are frozen once a file with that version exists anywhere;
  changes bump the version string.

## Conventions

- Tests: `~/Documents/Tonality/.venv/bin/python -m pytest tests/ -q` — no
  system-wide pytest on this machine; the Tonality venv carries pytest AND
  `mts` (the interpreter this project will need anyway). Package itself is
  stdlib-only.
- Validation is **total** (collect every error, don't stop at the first) —
  mirroring Tonality's `validate_ruleset` contract.

<!-- KNOWLEDGE-LOOP:START -->
## Self-Improving Knowledge Loop

Each session: read accumulated knowledge before acting, write distilled knowledge
after. This meta-layer sits on top of my primary role and never overrides it.

### Every session
1. **ORIENT** — Read INDEX.md in full (kept small on purpose). Pull ONLY the matching
   entries from LIBRARY.md into context. Never load all of LIBRARY by default.
2. **ACT** — Do the work, applying retrieved lessons. If a lesson proves wrong,
   correcting it outranks adding a new one.
3. **REFLECT** — Ask: "What did I learn that a future session needs and could not
   cheaply re-derive?" A lesson qualifies only if durable, evidenced (tied to a
   concrete trigger), and non-obvious. If nothing qualifies, write nothing.
4. **WRITE (atomic)** — Append the lesson to LIBRARY.md and a one-line pointer to
   INDEX.md in the same change. New lessons enter as `tier: candidate`; promote to
   `canonical` only on a second independent occurrence or human review.

### Write gate (anti-poisoning)
This loop feeds its own output back as input, so a wrong lesson, written once, is
retrieved and reinforced forever. Therefore: prefer not writing over writing
unverified; every lesson states what would falsify it; if a retrieved lesson
contradicts present evidence, trust the evidence and demote the lesson.

### Consolidation (periodic)
When LIBRARY exceeds ~30 entries, merge duplicates, delete superseded entries,
promote recurring candidates, tighten tags. Refactor it like code; don't grow it
like a log.

### LIBRARY entry template
`[Lxxxx] <title> | tier | added: YYYY-MM-DD | tags: … | lesson: … | evidence: … | falsifier: … | supersedes: …`
<!-- KNOWLEDGE-LOOP:END -->
