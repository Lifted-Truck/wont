"""Tests for the audition harness build (2026-07-08): the Wend client seam
(in-process transport, D16), the sweep/save server helpers, and a full
capture -> save -> reload round-trip over REAL generated music.

The Wend-dependent tests skip cleanly if Wend is not importable, so the pure
suite still runs elsewhere; on the Tonality venv (the mandated interpreter,
L0001) Wend imports and they run for real. Determinism is the throughline —
every wont core guarantee (seeded, no wall-clock, reproducible) must hold
through the client too.
"""

import pytest

from wont.scenario import Scenario
from wont.generate import GeneratedRun
from wont.clients.wend import (
    WendClient, resolve_ruleset_text, _WEND_IMPORT_ERROR,
)
from wont import loader

needs_wend = pytest.mark.skipif(
    _WEND_IMPORT_ERROR is not None,
    reason=f"Wend not importable ({_WEND_IMPORT_ERROR!r})",
)


# -- ruleset resolution (no Wend needed for inline; builtin needs the import) --

@needs_wend
def test_resolve_builtin_ruleset_is_wend_dsl():
    text = resolve_ruleset_text([{"ref": "wend:builtin"}])
    assert isinstance(text, str) and "rule " in text          # real Wend DSL

@needs_wend
def test_resolve_inline_dsl_is_verbatim():
    dsl = "config:\n  bars: 4\nrule r:\n  when tension < 1:\n    stay() weight 1.0\n"
    assert resolve_ruleset_text([{"dsl": dsl}]) == dsl

@needs_wend
def test_resolve_empty_falls_back_to_builtin():
    assert "rule " in resolve_ruleset_text([])                 # working default, not a crash


# -- the Wend client seam ---------------------------------------------------

@needs_wend
def test_client_generate_is_deterministic():
    c = WendClient()
    cfg = {"harmonic_motion": 0.3, "chord_voices": 5.0, "surface": "block"}
    a = c.generate_run(cfg, seed=11)
    b = c.generate_run(cfg, seed=11)
    assert a.events == b.events and a.trace == b.trace         # byte-identical (D16 promise)
    assert a.config == b.config

@needs_wend
def test_client_effective_config_keeps_real_fields_and_coerces():
    c = WendClient()
    # a bogus axis is dropped; chord_voices (sampled float) coerced to int; bars int.
    gen = c.generate_run({"chord_voices": 4.7, "not_a_wend_field": 99}, seed=1)
    assert "not_a_wend_field" not in gen.config
    assert gen.config["chord_voices"] == 5 and isinstance(gen.config["chord_voices"], int)
    assert isinstance(gen.config["bars"], int)
    # a rich arrangement so the listener auditions music, not a bare spine
    assert set(gen.events) <= {"chords", "bass", "topline", "drums"}
    assert "chords" in gen.events

@needs_wend
def test_client_events_are_schema_shaped():
    gen = WendClient().generate_run({}, seed=3)
    for part, evs in gen.events.items():
        for ev in evs:
            assert len(ev) == 4                                # [onset, dur, midi, vel]
            onset, dur, midi, vel = ev
            assert onset >= 0 and dur > 0 and 0 <= midi <= 127


# -- server helpers: sweep + save routing -----------------------------------

@needs_wend
def test_harness_sweep_generates_distinct_valid_runs():
    from harness.serve import Harness
    h = Harness()
    res = h.do_sweep("lofi-lounge", n=4, method="quasi", seed=0)
    assert res["count"] == 4
    ids = [r["run_id"] for r in res["runs"]]
    assert len(set(ids)) == 4                                  # distinct configs -> distinct ids
    r0 = res["runs"][0]
    assert r0["events"] and r0["bars"] and r0["bpm"] == 96
    assert r0["summary"]["notes"]["chords"] > 0

@needs_wend
def test_full_capture_save_reload_round_trip(tmp_path):
    """The whole loop over real music: generate -> dial -> lag-shift -> save ->
    reload -> validate. The provenance chain (scenario tag + fingerprint) that
    makes feedback recallable (D14) must survive the disk round-trip."""
    from harness.serve import assemble_labeled_run
    sc = Scenario(scenario_id="lofi-lounge",
                  seed_rulesets=[{"ref": "wend:builtin"}])
    gen = WendClient(resolve_ruleset_text(sc.seed_rulesets)).generate_run(
        {"harmonic_motion": 0.4}, seed=7)
    raw = [[b, round(-1 + 2 * b / 15, 2)] for b in range(16)]   # a ramp
    run = assemble_labeled_run(sc, gen, raw, scopes=["harmony"])
    path = loader.save_run(run, tmp_path)
    reloaded = loader.load_run(path)                            # validates on load
    assert reloaded.events == gen.events                       # music survived
    assert reloaded.satisfaction.lag_bars == 2
    assert reloaded.satisfaction.samples[0] == [0, -1.0]       # back-shifted 2 bars
    assert reloaded.scopes == ["harmony"]
    assert any(n.startswith("scenario:lofi-lounge") for n in reloaded.notes)
    assert any(n.startswith("scenario_fp:") for n in reloaded.notes)

@needs_wend
def test_do_save_routes_to_scenario_feedback_dir(tmp_path):
    """do_save writes into the scenario's feedback_dir. Inject a scenario whose
    feedback_dir is an absolute tmp path (os.path.join keeps it absolute) so the
    real routing is exercised without writing into the repo."""
    from harness.serve import Harness
    h = Harness()
    sc = Scenario(scenario_id="tmp-scn", feedback_dir=str(tmp_path),
                  seed_rulesets=[{"ref": "wend:builtin"}])
    h._scenarios[sc.scenario_id] = sc
    gen = h.client_for(sc).generate_run({}, seed=2)
    from wont.schema import compute_run_id
    rid = compute_run_id({"name": "wend", "version": h.client_for(sc).version},
                         gen.ruleset_text, gen.config, gen.seed)
    h._runs[rid] = (sc.scenario_id, gen)
    out = h.do_save(rid, [[0, 0.5], [1, 0.7]], ["rhythm"])
    saved = list(tmp_path.glob("*.labeled-run.json"))
    assert len(saved) == 1
    assert out["run_id"] in saved[0].name


# -- the assembler tolerates a client-less GeneratedRun (no Wend needed) -----

def test_assembler_pure_without_wend():
    from harness.serve import assemble_labeled_run
    sc = Scenario(scenario_id="lofi-lounge")
    gen = GeneratedRun(ruleset_text="rules{}", config={"seed": 1}, seed=1,
                       trace={"steps": []}, events={"chords": [[0.0, 4.0, 60, 80]]})
    run = assemble_labeled_run(sc, gen, [[2, 0.8]], scopes=[])
    run.validate()
    assert run.events == {"chords": [[0.0, 4.0, 60, 80]]}
    assert run.scopes == []                                    # global rating (D12 default)
