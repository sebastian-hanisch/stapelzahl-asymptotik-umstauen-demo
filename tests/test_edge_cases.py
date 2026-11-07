"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

import pytest

import sza_algorithm as A
import sza_constants as C
import sza_evaluation as ev
import sza_presets as P
from sza_scenario import make_bay


def _row(seed, lb1, lb2, greedy, opt=None):
    return {"seed": seed, "lb1": lb1, "lb2": lb2, "greedy": greedy, "opt": opt}


def test_sample_stats_by_hand_without_the_optimum():
    rows = [_row(0, 4, 5, 6), _row(1, 2, 2, 2), _row(2, 6, 7, 9), _row(3, 4, 4, 4)]
    s = ev.sample_stats(rows)
    assert s["n"] == 4 and s["lb1"] == 4 and s["lb2"] == 4.5 and s["greedy"] == 5.25 and "exact" not in s
    assert s["rel_gap"] == pytest.approx(5.25 / 4 - 1) and s["rel_gap_lb2"] == pytest.approx(5.25 / 4.5 - 1) and s["abs_gap"] == 1.25
    assert s["greedy_eq_lb1"] == 2 and s["greedy_eq_lb2"] == 2 and s["max_gap"] == 3


def test_sample_stats_with_the_optimum_and_a_capped_bay():
    rows = [_row(0, 4, 5, 6, 5), _row(1, 2, 2, 2, 2), _row(2, 6, 7, 9, None), _row(3, 4, 4, 4, 4)]
    e = ev.sample_stats(rows)["exact"]
    assert e["n"] == 3 and e["capped"] == 1                                     # die Bucht ohne Optimum fehlt in den exakten Kennzahlen
    assert e["opt"] == pytest.approx(11 / 3) and e["lb1"] == pytest.approx(10 / 3) and e["greedy"] == pytest.approx(4.0)
    assert e["opt_rel"] == pytest.approx(0.1) and e["greedy_rel"] == pytest.approx(4 / (11 / 3) - 1)
    assert e["opt_eq_lb1"] == 2 and e["opt_eq_lb2"] == 3 and e["greedy_eq_opt"] == 2 and e["violations"] == 0


def test_a_violated_order_is_counted():
    rows = [_row(0, 4, 5, 6, 3)]                                                 # Optimum unter LB1: so etwas darf nie vorkommen, die Zählung würde es melden
    assert ev.sample_stats(rows)["exact"]["violations"] == 1
    assert ev.sample_stats([_row(0, 4, 5, 6, 7)])["exact"]["violations"] == 1    # Optimum über der Regel


def test_a_sample_without_blockers_has_no_relative_gap():
    s = ev.sample_stats([_row(0, 0, 0, 0), _row(1, 0, 0, 0)])
    assert s["rel_gap"] is None and s["rel_gap_lb2"] is None and s["abs_gap"] == 0
    kind, text = ev.verdict_gap(s, "x")
    assert kind == "info" and text == "x: Die Stichprobe hat keine Blocker (Untergrenze 0); es gibt nichts zu vergleichen."


def test_analysis_is_exact_only_up_to_the_container_limit():
    small = ev.analyse(ev.Settings(8, 3, 2, 20, 0))
    big = ev.analyse(ev.Settings(9, 3, 2, 20, 0))
    assert small.exact and "exact" in small.stats and C.EXACT_MAX_CONTAINERS == 24
    assert not big.exact and "exact" not in big.stats and ev.exact_line(big.stats) is None
    assert len(small.rows) == 20 and small.rows[0]["seed"] == 0 and small.rows[-1]["seed"] == 19 and small.height == 5
    assert small.first_bay == make_bay(8, 3, 0) and len(small.first_bay) == 8


def test_snap_moves_values_to_the_nearest_step_or_the_bounds():
    assert P.snap("stacks_slider", 7) == 6 and P.snap("stacks_slider", 9) == 8 and P.snap("stacks_slider", 14) == 12 and P.snap("stacks_slider", 100) == 48 and P.snap("stacks_slider", 1) == 3
    assert P.snap("bays_slider", 80) == 100 and P.snap("bays_slider", 35) == 20 and P.snap("bays_slider", 5) == 20
    assert P.snap("layers_slider", 9) == 5 and P.snap("layers_slider", 0) == 2 and P.snap("seed_input", -3) == 0 and P.snap("seed_input", 10 ** 9) == C.SEED_MAX
    assert P.snap("stacks_slider", 11) == 10                                      # genau in der Mitte zwischen 10 und 12: die kleinere Stufe


def test_number_formats():
    assert ev.num(5) == "5" and ev.num(1234) == "1 234"
    assert ev.dec(5.0) == "5" and ev.dec(10.42) == "10,42" and ev.dec(0.3333) == "0,33" and ev.dec(4.999999999) == "5" and ev.dec(1234.5) == "1 234,50"
    assert ev.percent_text(0.0259) == "2,6 %" and ev.percent_text(0.473) == "47 %" and ev.percent_text(0.05) == "5,0 %" and ev.percent_text(0.1) == "10 %"
    assert ev.ratio3(0.4731) == "0,473" and ev.ratio3(0.0) == "0,000" and ev.ratio3(0.0056) == "0,006"


def test_exact_line_with_a_capped_bay():
    rows = [_row(0, 4, 5, 6, 5), _row(1, 2, 2, 2, None)]
    line = ev.exact_line(ev.sample_stats(rows))
    assert line.startswith("Gerechnet (Optimum aus der Suche, 1 von 2 Buchten, 1 am Knotenlimit): Optimum im Mittel 5, Untergrenze 4, Regel 6.")
    assert "Optimum im Mittel 5, Untergrenze 4, Regel 6" in line and "die Regel trifft das Optimum in 0 von 1 Buchten, die Zählung der Blocker in 0." in line
