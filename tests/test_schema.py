"""Synthetic-example tests for the labeled-run schema + loader.

The synthetic run mimics what Wend's Phase E.2 capture would emit: a
Wend-shaped trace (bar snapshots, fired rules), a .wend ruleset text, a
config dict, a seed, and a dial curve over 8 bars — but nothing here
depends on Wend, which is the point (any Tonality client can produce one).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from wont import (
    SCHEMA_VERSION,
    LabeledRun,
    SatisfactionCurve,
    ValidationError,
    compute_run_id,
    load_corpus,
    load_run,
    save_run,
)


def synthetic_run(seed: int = 41) -> LabeledRun:
    """A Wend-flavored labeled run, built by hand."""
    trace = {
        "seed": seed,
        "ruleset": "meadow",
        "steps": [
            {
                "bar": b,
                "snapshot": {"key": "C major", "chord": "I", "meter": "4/4",
                             "hyper_pos": b % 4, "tension": 0.2, "margin": 0.31},
                "matched_rules": ["drift", "cadence_pull"],
                "fired_rule": "drift" if b % 4 else "cadence_pull",
                "chosen_action": "step_fifthward",
                "action_args": {},
                "rng_draw": 0.5,
                "surprise": 0.1,
                "budget_after": 3.0 - 0.1 * b,
                "evidence": {},
                "notes": [],
            }
            for b in range(8)
        ],
    }
    return LabeledRun(
        client={"name": "wend", "version": "0.9"},
        engine_pins={"key_profile": "kk-1982.1"},
        ruleset_text="ruleset meadow:\n  when margin < 0.1 -> prefer step_fifthward\n",
        config={"tempo": 96, "parts": ["bass", "topline"], "surprise_budget": 3.0},
        seed=seed,
        trace=trace,
        satisfaction=SatisfactionCurve(
            samples=[[0, 0.5], [1, 0.5], [2, 0.7], [3, 0.7], [4, 0.9],
                     [5, 0.8], [6, 0.3], [7, 0.2]],
            value_min=0.0,
            value_max=1.0,
            lag_bars=1,
        ),
        scopes=["rhythm", "note_path"],
        events={
            "topline": [[0.0, 1.0, 60], [1.0, 0.5, 62, 96], [1.5, 0.5, 64, 96, "t1c1"]],
            "bass": [[0.0, 2.0, 36, 80]],
        },
        notes=["synthetic example for schema tests"],
    )


# -- identity ---------------------------------------------------------------

def test_run_id_is_deterministic_and_fingerprint_only():
    a, b = synthetic_run(), synthetic_run()
    assert a.computed_run_id() == b.computed_run_id()
    # satisfaction/trace changes do NOT change identity (D4)
    b.satisfaction.samples[0][1] = 0.9
    b.trace["steps"] = []
    assert a.computed_run_id() == b.computed_run_id()
    # any fingerprint change does
    assert synthetic_run(seed=42).computed_run_id() != a.computed_run_id()
    c = synthetic_run()
    c.config["tempo"] = 120
    assert c.computed_run_id() != a.computed_run_id()
    # and the hash is stable across dict key order
    reordered = dict(reversed(list(synthetic_run().config.items())))
    assert compute_run_id(a.client, a.ruleset_text, reordered, a.seed) == \
        compute_run_id(a.client, a.ruleset_text, a.config, a.seed)


def test_validate_verifies_a_present_run_id():
    run = synthetic_run()
    run.run_id = run.computed_run_id()
    run.validate()  # ok
    run.seed = 999  # fingerprint changed after id assignment
    with pytest.raises(ValidationError) as exc:
        run.validate()
    assert any("does not match the fingerprint" in e for e in exc.value.errors)


# -- round-trip ---------------------------------------------------------------

def test_json_round_trip_is_lossless():
    run = synthetic_run()
    run.validate()
    back = LabeledRun.from_json(run.to_json())
    back.validate()
    assert back.to_dict() == run.to_dict()
    assert back.run_id == run.computed_run_id()
    assert back.schema_version == SCHEMA_VERSION
    assert back.satisfaction.lag_bars == 1
    assert back.events["topline"][2] == [1.5, 0.5, 64, 96, "t1c1"]


# -- total validation ----------------------------------------------------------

def test_validation_is_total_and_catches_each_problem():
    run = synthetic_run()
    run.seed = "not-an-int"
    run.ruleset_text = ""
    run.satisfaction.samples = [[0, 0.5], [2, 1.5], [1, 0.5], [-1, 0.2]]
    run.events["topline"].append([0.0, 0.0, 300])
    with pytest.raises(ValidationError) as exc:
        run.validate()
    errors = "\n".join(exc.value.errors)
    assert "seed must be an int" in errors
    assert "ruleset_text must be a non-empty string" in errors
    assert "outside declared range" in errors          # value 1.5
    assert "non-decreasing" in errors                  # bar 1 after 2
    assert "bar must be >= 0" in errors                # bar -1
    assert "dur_beats must be > 0" in errors
    assert "midi must be an int in 0..127" in errors
    assert len(exc.value.errors) >= 7                  # all reported at once


def test_unknown_schema_version_is_rejected():
    run = synthetic_run()
    run.schema_version = "wont.labeled-run.99"
    with pytest.raises(ValidationError) as exc:
        run.validate()
    assert any("schema_version" in e for e in exc.value.errors)


def test_empty_curve_is_rejected():
    run = synthetic_run()
    run.satisfaction.samples = []
    with pytest.raises(ValidationError):
        run.validate()


def test_events_are_optional():
    run = synthetic_run()
    run.events = None
    run.validate()
    d = run.to_dict()
    assert "events" not in d
    LabeledRun.from_dict(d).validate()


# -- loader ---------------------------------------------------------------------

def test_save_load_run_and_corpus(tmp_path):
    corpus_dir = tmp_path / "corpus"
    p1 = save_run(synthetic_run(seed=41), corpus_dir)
    p2 = save_run(synthetic_run(seed=42), corpus_dir)
    assert p1 != p2 and p1.name.endswith(".labeled-run.json")

    one = load_run(p1)
    assert one.seed == 41 and one.client["name"] == "wend"

    runs = load_corpus(corpus_dir)
    assert len(runs) == 2
    assert {r.seed for r in runs} == {41, 42}


def test_corpus_load_reports_every_bad_file(tmp_path):
    corpus_dir = tmp_path / "corpus"
    save_run(synthetic_run(seed=41), corpus_dir)
    # one corrupt file, one invalid-schema file
    (corpus_dir / f"bad1{'.labeled-run.json'}").write_text("{not json", encoding="utf-8")
    broken = synthetic_run(seed=43).to_dict()
    del broken["seed"]
    (corpus_dir / "bad2.labeled-run.json").write_text(json.dumps(broken), encoding="utf-8")

    with pytest.raises(ValidationError) as exc:
        load_corpus(corpus_dir)
    errors = "\n".join(exc.value.errors)
    assert "bad1" in errors and "not valid JSON" in errors
    assert "bad2" in errors and "seed must be an int" in errors
