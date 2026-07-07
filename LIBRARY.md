# LIBRARY — durable, evidence-backed lessons

> Entries follow the template in CLAUDE.md's knowledge-loop block. Candidates
> promote to canonical on a second independent occurrence or human review.
> Refactor like code; don't grow like a log.

<a id="L0001"></a>
[L0001] Tonality venv is the working interpreter | candidate | added: 2026-07-07 |
tags: env-tooling |
lesson: No Python on this Mac has pytest system-wide (checked /usr/bin,
homebrew 3.12/3.13, Framework 3.13). `~/Documents/Tonality/.venv/bin/python`
has pytest 8.4.2 AND `mts` importable — use it for wont's tests and any
engine-touching script; don't burn time probing interpreters again. |
evidence: this setup session — 4 interpreters probed, all ModuleNotFoundError;
Tonality venv ran the 9-test suite in 0.05s. |
falsifier: a wont-local venv is created, or pytest appears in a system
interpreter / the Tonality venv is rebuilt without it. |
supersedes: —
