"""Tests for the 2026-07-08 scaffold: capture time-shift, scenario schema,
quasi-random sampler, and the harness assembler. Pure/deterministic — the same
bar guarantees the rest of wont holds to (no wall-clock, seeded)."""

import json
import os

from wont.capture import compensate_lag, build_curve, DEFAULT_LAG_BARS
from wont.scenario import Scenario
from wont.generate import ParameterSpace, sample, wend_starter_space


# -- capture: the time-shift ------------------------------------------------

def test_compensate_lag_shifts_earlier_and_clamps():
    raw = [[0, 0.1], [1, 0.5], [2, -0.3], [3, 0.9]]
    out = compensate_lag(raw, 2)
    assert out == [[0, 0.1], [0, 0.5], [0, -0.3], [1, 0.9]]  # shifted back, clamped at 0


def test_compensate_lag_zero_is_identity():
    raw = [[0, 0.1], [4, 0.5]]
    assert compensate_lag(raw, 0) == [[0, 0.1], [4, 0.5]]


def test_compensate_lag_preserves_non_decreasing_bars():
    raw = [[b, 0.0] for b in range(10)]
    out = compensate_lag(raw, 3)
    bars = [b for b, _ in out]
    assert bars == sorted(bars)


def test_build_curve_stamps_lag_and_validates():
    curve = build_curve([[2, 0.4], [3, -0.6]], lag_bars=2)
    assert curve.lag_bars == 2
    assert curve.value_min == -1.0 and curve.value_max == 1.0
    assert curve.validate() == []          # schema-valid
    assert curve.samples == [[0, 0.4], [1, -0.6]]


def test_default_lag_is_two_bars():
    assert DEFAULT_LAG_BARS == 2            # D8


# -- scenario schema --------------------------------------------------------

def test_scenario_round_trip():
    sc = Scenario(scenario_id="test-genre", target="test",
                  parameter_space=wend_starter_space().to_dict())
    d = sc.to_dict()
    back = Scenario.from_dict(d)
    assert back.scenario_id == "test-genre"
    assert back.validate() == []
    assert back.fingerprint() == sc.fingerprint()   # stable


def test_scenario_rejects_bad_slug_and_range():
    bad = Scenario(scenario_id="Not A Slug",
                   capture={"value_min": 1.0, "value_max": -1.0, "lag_bars": 2})
    errs = bad.validate()
    assert any("slug" in e for e in errs)
    assert any("value_min" in e for e in errs)


def test_example_scenario_on_disk_is_valid():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(here, "..", "scenarios", "lofi-lounge.json"))
    sc = Scenario.from_dict(json.load(open(path)))
    assert sc.validate() == []
    assert sc.scenario_id == "lofi-lounge"


# -- generator: deterministic quasi-random ----------------------------------

def test_parameter_space_validates():
    assert wend_starter_space().validate() == []


def test_quasi_sample_is_deterministic_and_covers():
    space = ParameterSpace(axes={"a": {"kind": "range", "min": 0.0, "max": 1.0}})
    s1 = sample(space, 8, method="quasi", seed=0)
    s2 = sample(space, 8, method="quasi", seed=0)
    assert s1 == s2                         # reproducible
    vals = sorted(c["a"] for c in s1)
    assert vals[0] < 0.5 < vals[-1]         # spans the axis, not clustered


def test_random_sample_seed_varies_but_is_reproducible():
    space = ParameterSpace(axes={"a": {"kind": "range", "min": 0.0, "max": 1.0}})
    assert sample(space, 5, method="random", seed=1) == sample(space, 5, method="random", seed=1)
    assert sample(space, 5, method="random", seed=1) != sample(space, 5, method="random", seed=2)


def test_choice_and_int_axes_project_in_bounds():
    space = ParameterSpace(axes={
        "s": {"kind": "choice", "options": ["x", "y", "z"]},
        "n": {"kind": "int", "min": 3, "max": 6},
    })
    for c in sample(space, 20, method="quasi", seed=0):
        assert c["s"] in ("x", "y", "z")
        assert 3 <= c["n"] <= 6 and isinstance(c["n"], int)


# -- harness assembler (ready half of /save) --------------------------------

def test_assembler_builds_valid_scenario_tagged_run():
    from harness.serve import assemble_labeled_run
    from wont.generate import GeneratedRun
    sc = Scenario(scenario_id="lofi-lounge", client={"name": "wend", "version": "0"})
    gen = GeneratedRun(ruleset_text="rules{}", config={"seed": 1}, seed=1,
                       trace={"steps": []}, events=None)
    run = assemble_labeled_run(sc, gen, [[2, 0.8], [3, 0.9]], scopes=["harmony"])
    run.validate()                          # raises on any problem
    assert run.satisfaction.lag_bars == 2
    assert run.satisfaction.samples == [[0, 0.8], [1, 0.9]]
    assert any(n == "scenario:lofi-lounge" for n in run.notes)
    assert run.engine_pins.get("key_profile") == "kk-1982.1"
