"""Inhalt der App an festen Fällen (DEMO-PLAYBOOK §12): was im Ergebnis, in den Tabellen und in den Verdikten steht."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(preset=None):
    at = AppTest.from_file(APP, default_timeout=300)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    if preset:
        at.sidebar.button(key=f"preset_{preset}").click().run()
        assert not at.exception, [str(e) for e in at.exception]
    return at


def _text(at):
    return "\n".join(e.value for kind in (at.markdown, at.caption, at.info, at.success, at.warning) for e in kind)


def _metrics(at):
    return {m.label: (m.value, m.delta) for m in at.metric}


def test_default_page_has_the_sections_and_the_default_result():
    at = _run()
    subs = [s.value for s in at.subheader]
    assert [s for s in subs if s.startswith("🔬")] == ["🔬 Experiment: Wie schnell schrumpft die Lücke?", "🔬 Experiment: Absolut gegen relativ", "🔬 Experiment: Exakt gerechnet", "🔬 Experiment: Platz"]
    assert "🚧 Wo die Annahmen enden" in subs
    m = _metrics(at)
    assert m["Untergrenze LB1 (Mittel)"] == ("3,53", "LB2: 4,41") and m["Regel (Mittel)"][0] == "5,20" and m["Regel über LB1"] == ("47 %", "absolut 1,67 Hübe")
    assert m["Zählung beweist"] == ("19 von 100", "Regel = LB1") and m["Optimum (Mittel)"] == ("5,05", "100 Buchten gerechnet")
    assert [w.value.endswith("Die Lücke zwischen Untergrenze und Optimum ist hier noch groß.") for w in at.warning] == [True, True]     # Ergebnis und exakte Zelle 3 × 3


def test_default_page_tables_quote_the_stored_numbers():
    text = _text(_run())
    assert "| 3 | 0,240 | 0,473 | 0,730 | 0,978 |" in text and "| 48 | 0,006 | 0,014 | 0,033 | 0,067 |" in text and "| 16 | 0,027 | 0,051 | 0,110 | 0,187 |" in text
    assert "| 3 | 0,36 (133) | 1,64 (44) | 4,20 (3) | 8,08 (0) |" in text and "| 48 | 0,13 (174) | 0,76 (86) | 3,01 (21) | 8,75 (0) |" in text
    assert "| 12 × 3 (60) | 13,92 | 14,40 | 14,97 | 15,02 | 22 | 7,5 % | 0,3 % | 57 |" in text and "| 8 × 4 (59, 1 am Limit) |" in text
    assert "| 3 Lagen, 16 Stapel | 0,055 | 0,051 | 0,050 | 0,050 |" in text and "| 4 Lagen, 32 Stapel |" in text


def test_default_page_verdicts_for_the_default_layers():
    text = _text(_run())
    assert "3 Lagen: Die relative Lücke fällt von 47 % bei 3 Stapeln auf 1,4 % bei 48. Höchstens 5,0 % beträgt sie ab 24 Stapeln." in text
    assert "3 Lagen: Die relative Lücke fällt von 47 % auf 1,4 %, die absolute von 1,64 auf 0,76 Hübe;" in text and "Auch die absolute Lücke schrumpft." in text
    assert "3 × 3: Das Optimum liegt im Mittel 38 % über der Untergrenze" in text


def test_high_stacks_preset_shows_that_the_absolute_gap_stays():
    at = _run("Hohe Stapel (16 Stapel, 5 Lagen)")
    assert _metrics(at)["Zählung beweist"] == ("0 von 100", "Regel = LB1") and _metrics(at)["Optimum (Mittel)"][0] == "nicht gerechnet"
    text = _text(at)
    assert "5 Lagen: Die relative Lücke fällt von 98 % bei 3 Stapeln auf 6,7 % bei 48. Höchstens 5,0 % beträgt sie bis 48 Stapel nicht." in text
    assert any("Die absolute Lücke bleibt" in w.value for w in at.warning) and any("noch nicht scharf" in i.value for i in at.info)


def test_exact_preset_shows_the_live_optimum_line():
    at = _run("Exakt: 8 Stapel, 3 Lagen")
    text = _text(at)
    assert "Gerechnet (Optimum aus der Suche, 50 Buchten): Optimum im Mittel 10,38, Untergrenze 9,14, Regel 10,42." in text
    assert "die Regel trifft das Optimum in 48 von 50 Buchten, die Zählung der Blocker in 14." in text


@pytest.mark.parametrize("stacks,layers", [(48, 5), (5, 4)])
def test_cells_with_and_without_stored_exact_bands_do_not_crash(stacks, layers):
    at = _run()
    at.sidebar.select_slider(key="stacks_slider").set_value(stacks).run()
    at.sidebar.slider(key="layers_slider").set_value(layers).run()
    assert not at.exception
    assert any("wurde das Optimum nicht vorberechnet" in i.value for i in at.info)
