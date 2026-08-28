# wont

> **APPROVED by Julian, 2026-07-07.** "wont" (n., archaic):
> one's habit, custom, what one is accustomed to. Chosen to pair with sibling
> project **Wend** (to go one's way): Wend walks, wont learns what you are
> wont to like. Alternatives considered: `fain` (gladly, desirous), `lief`
> ("I'd as lief hear that again"). Rename is a one-commit operation — nothing
> downstream depends on the name yet (the Tonality intake branch would be
> re-filed under the new name).

**The satisfaction-loop learner** — a modular preference-learning system for
generative-music tools built on the [Tonality](../../../Tonality/) music-theory
engine.

## What it is

A user turns a **satisfaction dial** while a generated composition plays. The
time-stamped signal, aligned to bars via the client's trace, becomes labeled
training data for **classical ML** (Markov chain / bandit / logistic class —
explicitly no deep nets) that learns which rulesets and parameterizations
correlate with satisfaction, and biases future generation.

Two outputs, always:

1. **Oriented recommendations** — versioned, provenance-stamped **bias
   artifacts** that consumer generators apply deterministically (pinned
   artifact + seed reproduces exactly; nothing learns online inside a
   generator).
2. **A Tonality-readable data readout** — labeled/annotated datasets exported
   in Tonality's interchange vocabulary (`DatasetRecord`-style JSON with
   `SCHEMA_VERSION`, rulesets as DSL JSON), so humans and agents can run
   independent analysis with engine tools.

Modular by design: the feature vocabulary is **Tonality's, not bespoke**
(rule firings, conformance reports, melodic/rhythmic atoms, succession tags),
so the learner serves *any* Tonality client — Wend is the first, not the only.

## Status

**Audition harness BUILT** (2026-07-08, D13–D17); the learner is next and
**gated**. Start at [ROADMAP.md](ROADMAP.md) for what's next and the gate.
Built and tested end to end: the labeled-run schema + loader, the satisfaction
**time-shift** (`capture.py`), the **scenario** schema (`scenario.py`, frozen
`.1`), the deterministic quasi/random **sweep sampler** (`generate.py`), the
**Wend client** (`clients/wend.py`, in-process transport, D16), and the
**audition server + UI** (`harness/` — sweep, WebAudio playback, dial capture,
scenario-tagged save). **The learner itself is still deliberately not built** —
dialogue-first; per D11 its first slice is the synthetic recovery harness, not
the ML. The Tonality intake dialogue that gated it has resolved; the remaining
gate is Julian's go-ahead.

### Run the audition harness

```
~/Documents/Tonality/.venv/bin/python -m harness.serve   # -> http://127.0.0.1:8771
```

## Layout

```
README.md      this file
ROADMAP.md     >>> START HERE: phase-gated sequence + the learner gate
CLAUDE.md      agent pointers + gotchas
DESIGN.md      the design document (scopes, schemas, credit assignment, v1 plan)
DECISIONS.md   append-only decision log (D1-D19)
HANDOFF.md     the 2026-07-08 build-agent brief (historical launch context)
INDEX.md       knowledge-loop retrieval map (see CLAUDE.md's loop block)
LIBRARY.md     knowledge-loop lesson store
verify         the oracle: ./verify fast | full | report
wont/          the package
  schema.py    LabeledRun -- the labeled-run schema (frozen .1; validation, round-trip)
  loader.py    load/save labeled runs and corpora
  capture.py   dial signal -> lag-compensated SatisfactionCurve (the time-shift, D15)
  scenario.py  Scenario -- named training context (frozen .1, D14/D17)
  generate.py  ParameterSpace + deterministic quasi/random sampler + Client seam (D13)
  clients/     generator adapters (wend.py -- the only place that drives Wend, D16)
harness/       wont's audition GUI (serve.py HTTP server + index.html audition UI)
scenarios/     scenario JSONs (lofi-lounge.json -- worked example)
tests/
  test_schema.py     labeled-run round-trip + validation
  test_scaffold.py   capture / scenario / sampler / assembler (2026-07-08)
  test_harness.py    Wend client seam, sweep/save, full capture round-trip
```

## Running the tests

```
~/Documents/Tonality/.venv/bin/python -m pytest tests/ -q
```

(No system-wide pytest on this machine; the Tonality venv carries pytest and
`mts`.) Zero dependencies beyond the standard library. The
`mts` boundary module ([DESIGN.md](DESIGN.md) §6) does not exist yet — by
design.
