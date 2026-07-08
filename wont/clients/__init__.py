"""clients/ — adapters that let a generator implement the generate.Client seam.

One file per client. Each adapter is the ONLY place that knows how to drive its
generator; wont's learner never imports a client. Wend is first (wend.py).

Keeping these OUT of the learner is the same discipline as DESIGN.md §6's
`mts` boundary: a client adapter may shell out to or import its generator, but
the coupling stops at this directory.
"""
