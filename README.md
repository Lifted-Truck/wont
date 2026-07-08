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

**Harness-scaffold phase.** Julian greenlit wont's own GUI + generator +
scenarios (2026-07-08, D13–D15); the Wend agent prepared the launch pad. **Start
at [HANDOFF.md](HANDOFF.md).** Ready and tested: the labeled-run schema + loader,
the satisfaction **time-shift** (`capture.py`), the **scenario** schema
(`scenario.py`, draft), and the deterministic quasi/random **sweep sampler**
(`generate.py`). Stubs for the build-agent: the Wend client adapter
(`clients/wend.py`), the audition server + UI (`harness/`). **The learner itself
is still deliberately not built** — dialogue-first; per D11 its first slice is
the synthetic recovery harness, not the ML.

## Layout

```
README.md      this file
HANDOFF.md     >>> START HERE: the build-agent brief (mission, ready vs stubs, plan)
CLAUDE.md      agent pointers + gotchas
DESIGN.md      the design document (scopes, schemas, credit assignment, v1 plan)
DECISIONS.md   append-only decision log (D1–D15)
INDEX.md       knowledge-loop retrieval map (see CLAUDE.md's loop block)
LIBRARY.md     knowledge-loop lesson store
wont/          the package
  schema.py    LabeledRun — the labeled-run schema (frozen .1; validation, round-trip)
  loader.py    load/save labeled runs and corpora
  capture.py   dial signal -> lag-compensated SatisfactionCurve (the time-shift, D15)
  scenario.py  Scenario — named training context (draft schema, D14)
  generate.py  ParameterSpace + deterministic quasi/random sampler + Client seam (D13)
  clients/     generator adapters (wend.py — STUB, the only place that drives Wend)
harness/       wont's audition GUI (serve.py orchestration scaffold + index.html skeleton)
scenarios/     scenario JSONs (lofi-lounge.json — worked example)
tests/
  test_schema.py     labeled-run round-trip + validation
  test_scaffold.py   capture / scenario / sampler / assembler (2026-07-08)
```

## Running the tests

```
~/Documents/Tonality/.venv/bin/python -m pytest tests/ -q
```

(No system-wide pytest on this machine; the Tonality venv carries pytest and
`mts`.) Zero dependencies beyond the standard library. The
`mts` boundary module ([DESIGN.md](DESIGN.md) §6) does not exist yet — by
design.
