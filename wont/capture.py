"""capture.py — dial signal → lag-compensated SatisfactionCurve.

THE TIME-SHIFT (Julian, 2026-07-08; DECISIONS.md D15). A satisfaction spike or
valley always refers to something that JUST occurred, not the instant the dial
moved — a listener reacts a moment late. So the raw curve is shifted EARLIER in
time to align each label with the music that CAUSED it: a sample the dial
produced at bar B is credited to bar B - lag. This is the `lag_bars`
compensation the schema already carries (D8 fixed it client-side at 2 bars);
this module is the one place that applies it, so every wont client shifts the
same way and stamps how much.

Two consumers, one transform:
  - the GUI draws the curve shifted back so the user SEES labels sitting under
    their cause (harness/);
  - the saved LabeledRun stores the shifted samples with `lag_bars` stamped, so
    the learner trains on cause-aligned labels.

Deterministic, stdlib only. No wall-clock reads. The learner-side refinement —
searching for the lag that best explains a curve instead of a fixed prior
(DESIGN.md §8.1) — is a documented hook, NOT applied here; a fixed, declared
lag is the honest v1 (D8), and a stamped `lag_bars` lets the learner revisit.
"""

from __future__ import annotations

from .schema import SatisfactionCurve

# D8: reaction lag compensated client-side at a fixed 2 bars. The GUI may expose
# this as a knob; the default stays 2 so captures are comparable across sessions.
DEFAULT_LAG_BARS = 2


def compensate_lag(samples, lag_bars: int = DEFAULT_LAG_BARS):
    """Shift (bar, value) samples EARLIER by `lag_bars`, clamped at bar 0.

    Aligns each label to the music that caused it. Order is preserved (a
    constant subtraction + clamp keeps bars non-decreasing), so the result is
    schema-valid. `lag_bars=0` is the identity (raw signal).

    Returns a new list; does not mutate the input.
    """
    if lag_bars < 0:
        raise ValueError(f"lag_bars must be >= 0, got {lag_bars}")
    out = []
    for pair in samples:
        bar, value = pair[0], pair[1]
        out.append([max(0, int(bar) - lag_bars), float(value)])
    return out


def build_curve(
    raw_samples,
    *,
    value_min: float = -1.0,
    value_max: float = 1.0,
    lag_bars: int = DEFAULT_LAG_BARS,
) -> SatisfactionCurve:
    """Raw dial samples → a lag-compensated, schema-valid SatisfactionCurve.

    Defaults to the bipolar held-state dial (-1..+1) approved in D8. Applies the
    time-shift and stamps `lag_bars` so the learner knows the compensation
    already baked in. Raises via SatisfactionCurve.validate() semantics only
    when the caller chooses to validate the enclosing LabeledRun.
    """
    curve = SatisfactionCurve(
        samples=compensate_lag(raw_samples, lag_bars),
        value_min=value_min,
        value_max=value_max,
        lag_bars=lag_bars,
    )
    return curve


def display_shift(samples, lag_bars: int = DEFAULT_LAG_BARS):
    """Alias for compensate_lag, named for the GUI's drawing path — the graph is
    rendered with the same backshift so the user sees labels under their cause.
    """
    return compensate_lag(samples, lag_bars)
