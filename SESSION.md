# SESSION — wont

> Hot state. The only prior-session context the next session trusts. Written at
> close; superseded by the next close. Authority order: ROADMAP (what/when) >
> DESIGN (how) > this file (where we stopped).

**Closed:** 2026-08-28 · **branch:** `main` → PR `chore/session-2026-08-28`
**verify:** `fast` GREEN (exit 0) · `full` GREEN (exit 0), both run at close

## State summary

The **audition harness is built, tested, and running** — this session took it
from scaffold to working software:

- `wont/clients/wend.py` — the Wend seam, was a stub, now live (**in-process**
  transport, D16). Deterministic: one (ruleset_text, config, seed) →
  byte-identical music.
- `harness/serve.py` — was an orchestration scaffold whose `main()` raised; now
  a stdlib HTTP server on **:8771** (`/scenarios`, `/sweep`, `/save`). Fixed a
  scaffold path bug (`SCENARIO_DIR` had one `..` too many — it was silently
  returning zero scenarios).
- `harness/index.html` — was a TODO skeleton; now the full loop: sweep →
  WebAudio playback → per-bar dial capture → lag-shifted graph → save.
- Scenario schema **frozen** `1-draft` → `wont.scenario.1` (D17).
- `./verify` **created** (D20) — the repo had a vendored `.kit/` but no
  dispatcher, so its gates were inert. Now Layer-0 + Layer-E, both green.
- `ROADMAP.md` **created** — the phase-gated sequence and the learner gate.
- README de-drifted (it still claimed "Harness-scaffold phase").

Tests: **32 passing** (`~/Documents/Tonality/.venv/bin/python -m pytest tests/ -q`).
The Tonality venv is the mandated interpreter — no system pytest, and it alone
carries `mts` + importable `Wend` ([L0001]).

Also this session: the **Tonality dialogue closed**. The Markov-alignment notice
was bound (D18, [L0003]); `pieces = runs` was reopened for Wend, taken to
Tonality as brief-2, and **resolved by response-2** — scope-separation dissolves
the K-parallel-scoped-session problem ([L0004] canonical, [L0005]). Capture-data
versioning settled as a three-tier promotion model (D19).

## Next first move

**Start Phase 2 — open `wont/engine.py`**, the sole `mts`-importing boundary
module. Then: slicer (curve → liked/disliked spans) → corpus builder (one pooled
pseudo-piece per `(run, scope)`, never per-span) → the D11 synthetic-recovery
experiment. Exit criterion is pre-registered and Layer-0: on a seeded synthetic
corpus the recovered contrast must correlate with the injected utility above a
threshold fixed BEFORE the run.

**The learner gate is LIFTED** (D20b) — Julian approved at this close. Do not
re-ask; do read ROADMAP Phase 2 before starting.

## Open threads

- **Back up the capture dir.** `scenarios/*/runs/` is gitignored (D19 tier 1)
  and holds the one irreplaceable asset — frozen human listening time. No gate
  can protect it. Unconfirmed whether it sits on a synced path.
- **The §8 policy knobs** (slice threshold + hysteresis, min-span length,
  normalization) are decided AT the Phase-2 build, explicitly — not inherited
  from whatever the first implementation does.
- **Wend has not been told** about response-2's ruling, which lands on its own
  architecture: the D10 staging buffer is attribution + render-efficiency, NOT
  within-scope statistical power ([L0005]). Cross-repo notice owed
  (INTEGRATIONS.md governs; writes stay home).
- **Channel drafts** written into Tonality this session: `brief-2.md` (filed),
  `ack-per-run-pooling.md` (reported handled) — worth confirming both landed.
- **Name still provisional** (D1) — "wont" was approved in D8, README still
  carries the alternatives. Cosmetic; noted so it is not rediscovered.

## Traces

No trace directory in this repo. This session's evidence: `DECISIONS.md`
D16–D20, `REFLECTIONS.md` (2026-08-28 entries), `.harness/last-verify.json`
(local, gitignored), and the PR body.
