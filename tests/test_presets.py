"""Presets: jede Einstellung hat die Eigenschaft, für die sie steht (DEMO-PLAYBOOK §12), und die Hilfetexte nennen nur gemessene Zahlen."""

import pytest

import sza_constants as C
import sza_evaluation as ev
import sza_presets as P


def _analyse(name):
    p = C.PRESETS[name]
    return ev.analyse(ev.Settings(p["stacks"], p["layers"], p["extra"], p["bays"], p["seed"]))


def test_every_preset_is_inside_the_slider_bounds_and_on_a_step_and_has_help():
    for name, p in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            lo, hi = P.bounds(state_key)
            assert lo <= p[key] <= hi and P.snap(state_key, p[key]) == p[key], (name, key)
    assert set(C.PRESET_HELP) == set(C.PRESETS) and all(C.PRESET_HELP.values())


def test_few_stacks_leave_a_large_gap():
    a = _analyse("Wenige Stapel (3 Stapel, 3 Lagen)")
    s = a.stats
    assert a.exact and s["n"] == 100 and s["lb1"] == pytest.approx(3.53) and s["greedy"] == pytest.approx(5.2) and round(s["rel_gap"], 3) == 0.473 and ev.verdict_gap(s, "x")[0] == "warning"
    assert s["exact"]["opt"] == pytest.approx(5.05) and s["exact"]["violations"] == 0


def test_many_stacks_are_nearly_sharp():
    s = _analyse("Viele Stapel (32 Stapel, 3 Lagen)").stats
    assert s["lb1"] == pytest.approx(37.49) and s["greedy"] == pytest.approx(38.45) and round(s["rel_gap"], 3) == 0.026 and ev.verdict_gap(s, "x")[0] == "success" and "exact" not in s


def test_two_layers_are_sharp_at_16_stacks():
    s = _analyse("Zwei Lagen (16 Stapel, 2 Lagen)").stats
    assert round(s["rel_gap"], 3) == 0.025 and s["greedy_eq_lb1"] == 80 and ev.verdict_gap(s, "x")[0] == "success"


def test_high_stacks_keep_the_absolute_gap_and_the_count_never_proves_optimality():
    s = _analyse("Hohe Stapel (16 Stapel, 5 Lagen)").stats
    assert s["greedy_eq_lb1"] == 0 and round(s["abs_gap"], 1) == 8.0 and round(s["rel_gap"], 3) == 0.183 and ev.verdict_gap(s, "x")[0] == "info"


def test_exact_preset_computes_the_optimum_live():
    a = _analyse("Exakt: 8 Stapel, 3 Lagen")
    e = a.stats["exact"]
    assert a.exact and a.stats["n"] == 50 and e["n"] == 50 and e["capped"] == 0 and e["opt"] == pytest.approx(10.38) and e["greedy_eq_opt"] == 48 and e["violations"] == 0
    assert e["opt_eq_lb1"] == 14 and round(e["opt_rel"], 3) == 0.136


def test_the_default_settings_are_the_first_preset():
    assert {s: P.SETTING_SPECS[s].default for s in P.SETTING_SPECS} == {"stacks_slider": 3, "layers_slider": 3, "extra_slider": 2, "bays_slider": 100, "seed_input": 0}
    assert C.PRESETS["Wenige Stapel (3 Stapel, 3 Lagen)"] == {"stacks": 3, "layers": 3, "extra": 2, "bays": 100, "seed": 0}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_apply_preset_writes_every_setting(name, monkeypatch):
    state = {}
    monkeypatch.setattr(P.st, "session_state", state)
    P.apply_preset(name)
    assert {k: state[sk] for k, sk in P.PRESET_KEYS.items()} == {k: C.PRESETS[name][k] for k in P.PRESET_KEYS}
    assert P.aktives_preset() == name
