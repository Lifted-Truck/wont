# wont

> **PROVISIONAL NAME — awaiting Julian's approval.** "wont" (n., archaic):
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

**Design-dialogue phase.** Deliverables so far: this scaffold, [DESIGN.md](DESIGN.md),
a Tonality intake brief (filed on branch `wont-intake-brief` in the Tonality
repo), and the labeled-run schema + loader with tests. **The learner itself is
deliberately not built** — Julian's directive is dialogue before concrete
decisions; the schema/loader is the reversible, safe-pre-dialogue slice.

## Layout

```
README.md      this file
CLAUDE.md      agent pointers + gotchas
DESIGN.md      the design document (scopes, schemas, credit assignment, v1 plan)
DECISIONS.md   append-only decision log
INDEX.md       knowledge-loop retrieval map (see CLAUDE.md's loop block)
LIBRARY.md     knowledge-loop lesson store
wont/          the package
  schema.py    LabeledRun — the versioned labeled-run schema (validation, JSON round-trip)
  loader.py    load/save labeled runs and corpora
tests/
  test_schema.py   synthetic-example round-trip + validation tests
```

## Running the tests

```
~/Documents/Tonality/.venv/bin/python -m pytest tests/ -q
```

(No system-wide pytest on this machine; the Tonality venv carries pytest and
`mts`.) Zero dependencies beyond the standard library. The
`mts` boundary module ([DESIGN.md](DESIGN.md) §6) does not exist yet — by
design.
