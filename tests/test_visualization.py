"""Abbildungen an synthetischen Daten: Werte, Farben, gesperrte Achsen, Logarithmusachsen ohne add_hline (DEMO-PLAYBOOK §12)."""

import plotly.graph_objects as go
import pytest

import sza_constants as C
import sza_evaluation as ev
import sza_visualization as V


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def test_blocker_cells_by_hand():
    assert V.blocker_cells(((1, 5), (2, 3), (4, 6))) == {(0, 1), (1, 1), (2, 1)}
    assert V.blocker_cells(((1, 2, 3), (), (4,))) == {(0, 1), (0, 2)} and V.blocker_cells(((5, 3), (2, 1))) == set()


def test_bay_chart_colours_texts_and_the_height_line():
    fig = V.build_bay(((1, 5), (2, 3), (4, 6)), 4, target=1)
    assert _locked(fig) and len(fig.data) == 4 and list(fig.layout.yaxis.range) == [0, 4.35]
    assert list(fig.data[0].marker.color) == [C.COLOR_TARGET, C.COLOR_CELL, C.COLOR_CELL] and list(fig.data[0].text) == ["1", "2", "4"]
    assert list(fig.data[1].marker.color) == [C.COLOR_BLOCK] * 3 and list(fig.data[2].y) == [0, 0, 0] and [s.y0 for s in fig.layout.shapes] == [4]


def _asym(f):
    return {ev.cell_key(s, l): {"rel_gap": f(s, l), "abs_gap": 10.0 * l + s / 100} for s in C.STACK_OPTIONS for l in (2, 3, 4, 5)}


def test_curve_chart_is_log_log_with_one_line_per_layer_and_the_threshold_as_a_trace():
    fig = V.build_curve(_asym(lambda s, l: l / s))
    assert _locked(fig) and fig.layout.xaxis.type == "log" and fig.layout.yaxis.type == "log" and not fig.layout.shapes
    assert [t.name for t in fig.data] == ["2 Lagen", "3 Lagen", "4 Lagen", "5 Lagen", "Schwelle „scharf“"]
    assert list(fig.data[0].x) == list(C.STACK_OPTIONS) and list(fig.data[1].y)[0] == pytest.approx(100.0) and list(fig.data[3].y)[-1] == pytest.approx(100.0 * 5 / 48)
    assert list(fig.data[4].y) == [5.0, 5.0] and [t.line.color for t in fig.data[:4]] == [C.COLOR_LINES[l] for l in (2, 3, 4, 5)]
    assert list(fig.layout.xaxis.tickvals) == list(C.STACK_OPTIONS)


def test_absolute_chart_is_linear_in_y_from_zero():
    fig = V.build_abs(_asym(lambda s, l: 0.1))
    assert _locked(fig) and fig.layout.yaxis.rangemode == "tozero" and fig.layout.xaxis.type == "log" and fig.layout.yaxis.type is None
    assert list(fig.data[2].y)[0] == pytest.approx(40.03) and len(fig.data) == 4


def test_exact_chart_is_ordered_by_layers_then_stacks_and_in_percent():
    cells = {"8,3": {"exact": {"opt_rel": 0.14, "greedy_rel": 0.005}}, "3,4": {"exact": {"opt_rel": 0.57, "greedy_rel": 0.063}}, "4,2": {"exact": {"opt_rel": 0.148, "greedy_rel": 0.0}},
             "3,3": {"exact": {"opt_rel": 0.381, "greedy_rel": 0.03}}}
    fig = V.build_exact(cells)
    assert _locked(fig) and list(fig.data[0].x) == ["4 × 2", "3 × 3", "8 × 3", "3 × 4"]
    assert list(fig.data[0].y) == pytest.approx([14.8, 38.1, 14.0, 57.0]) and list(fig.data[1].y) == pytest.approx([0.0, 3.0, 0.5, 6.3]) and [t.name for t in fig.data] == ["Optimum über der Untergrenze", "Regel über dem Optimum"]


def test_all_figures_are_plotly_figures():
    asym = _asym(lambda s, l: 0.1)
    assert all(isinstance(f, go.Figure) for f in (V.build_bay(((1,),), 2), V.build_curve(asym), V.build_abs(asym)))
