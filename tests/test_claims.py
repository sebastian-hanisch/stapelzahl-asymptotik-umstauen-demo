"""Aussagen der Demo und des READMEs gegen die vorberechneten Bänder und gegen eine frische Nachrechnung kleiner Zellen (DEMO-PLAYBOOK §5, §12).

Alle Größen sind deterministisch (feste Seeds, keine Zeiten) und müssen bei der Nachrechnung gleich sein."""

import pytest

import sza_constants as C
import sza_evaluation as ev


def K(s, l):
    return ev.cell_key(s, l)


def _bands():
    return ev.load_bands()


def test_the_stored_cells_cover_exactly_the_cells_of_the_constants():
    b = _bands()
    assert set(b["asym"]) == {K(s, l) for s in C.STACK_OPTIONS for l in (2, 3, 4, 5)} and all(c["n"] == C.ASYM_BAYS for c in b["asym"].values())
    assert set(b["exakt"]) == {K(s, l) for s, l in C.EXACT_CELLS} and all(c["n"] == C.EXACT_BAYS for c in b["exakt"].values())
    assert set(b["platz"]) == {ev.platz_key(l, e, s) for l in C.PLATZ_LAYERS for e in (1, 2, 3, 4) for s in C.PLATZ_STACKS}


def test_the_relative_gap_falls_with_the_number_of_stacks_for_every_layer_count():
    asym = _bands()["asym"]
    for l in (2, 3, 4, 5):
        gaps = [asym[K(s, l)]["rel_gap"] for s in C.STACK_OPTIONS]
        assert all(a > b for a, b in zip(gaps, gaps[1:])), (l, gaps)                    # streng monoton über alle 11 Stufen
    for s in C.STACK_OPTIONS:                                                            # und wächst mit den Lagen
        gaps = [asym[K(s, l)]["rel_gap"] for l in (2, 3, 4, 5)]
        assert all(a < b for a, b in zip(gaps, gaps[1:])), (s, gaps)


def test_the_numbers_the_readme_quotes_for_the_relative_gap():
    asym = _bands()["asym"]
    assert [round(asym[K(s, 3)]["rel_gap"], 3) for s in (3, 8, 24, 48)] == [0.473, 0.139, 0.031, 0.014]
    assert [round(asym[K(s, 5)]["rel_gap"], 3) for s in (3, 16, 48)] == [0.978, 0.187, 0.067] and round(asym[K(48, 2)]["rel_gap"], 3) == 0.006
    assert {l: ev.sharp_from(asym, l) for l in (2, 3, 4, 5)} == {2: 10, 3: 24, 4: 32, 5: None}


def test_the_absolute_gap_and_the_exact_hits_the_readme_quotes():
    asym = _bands()["asym"]
    assert [asym[K(s, 3)]["abs_gap"] for s in (3, 8, 16, 48)] == pytest.approx([1.635, 1.29, 0.95, 0.755], abs=1e-9)
    assert [asym[K(s, 3)]["greedy_eq_lb1"] for s in (3, 8, 16, 48)] == [44, 49, 70, 86]
    assert [asym[K(s, 5)]["abs_gap"] for s in (3, 8, 16, 48)] == pytest.approx([8.075, 7.37, 8.22, 8.745], abs=1e-9) and [asym[K(s, 5)]["greedy_eq_lb1"] for s in (3, 8, 16, 48)] == [0, 0, 0, 0]
    assert asym[K(48, 5)]["abs_gap"] >= 0.5 * asym[K(3, 5)]["abs_gap"] and asym[K(48, 3)]["abs_gap"] < 0.5 * asym[K(3, 3)]["abs_gap"]


def test_the_exact_cells_satisfy_the_order_and_the_numbers_the_readme_quotes():
    ex = _bands()["exakt"]
    for c in ex.values():
        assert c["exact"]["violations"] == 0 and c["exact"]["capped"] <= 1 and c["exact"]["n"] + c["exact"]["capped"] == 60
        assert c["exact"]["opt_rel"] <= c["rel_gap"] + 1e-9 or c["exact"]["capped"] == 1                    # das Optimum liegt nie weiter über LB1 als die Regel
    assert [round(ex[K(s, 3)]["exact"]["opt_rel"], 3) for s in (3, 6, 12)] == [0.381, 0.166, 0.075]
    assert round(ex[K(3, 4)]["exact"]["greedy_rel"], 3) == 0.063 and round(ex[K(12, 3)]["exact"]["greedy_rel"], 3) == 0.003 and ex[K(8, 4)]["exact"]["capped"] == 1
    assert max(c["exact"]["greedy_rel"] for c in ex.values()) < 0.1 and ex[K(12, 2)]["exact"]["greedy_eq_opt"] == 60


def test_the_platz_numbers_the_readme_quotes():
    p = _bands()["platz"]
    assert [round(p[ev.platz_key(3, e, 16)], 3) for e in (1, 2, 3, 4)] == [0.055, 0.051, 0.05, 0.05]
    assert all(p[ev.platz_key(l, 1, s)] >= p[ev.platz_key(l, 2, s)] >= p[ev.platz_key(l, 3, s)] >= p[ev.platz_key(l, 4, s)] for l in (3, 4) for s in (4, 8, 16, 32))


@pytest.mark.parametrize("stacks,layers", [(3, 3), (8, 2), (16, 3)])
def test_a_fresh_recomputation_of_cells_reproduces_the_stored_band(stacks, layers):
    stored = _bands()["asym"][K(stacks, layers)]
    fresh = ev.sample_stats(ev.bay_rows(stacks, layers, C.DEFAULT_EXTRA, range(C.ASYM_BAYS)))
    assert fresh == stored


def test_a_fresh_recomputation_of_an_exact_cell_reproduces_the_stored_band():
    stored = _bands()["exakt"][K(6, 3)]
    fresh = ev.sample_stats(ev.bay_rows(6, 3, C.DEFAULT_EXTRA, range(C.EXACT_BAYS), True, C.EXACT_CAP_BAND))
    assert fresh == stored


def test_a_fresh_recomputation_of_a_platz_cell_reproduces_the_stored_value():
    assert ev.sample_stats(ev.bay_rows(16, 3, 1, range(C.ASYM_BAYS)))["rel_gap"] == _bands()["platz"][ev.platz_key(3, 1, 16)]
