"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import sza_constants as C
import sza_evaluation as ev


def _stats(lb1=10.0, greedy=10.4, n=100, abs_gap=None, eq=40, **extra):
    s = {"n": n, "lb1": lb1, "lb2": lb1 + 0.2, "greedy": greedy, "rel_gap": greedy / lb1 - 1, "rel_gap_lb2": 0.0, "abs_gap": greedy - lb1 if abs_gap is None else abs_gap,
         "greedy_eq_lb1": eq, "greedy_eq_lb2": eq, "max_gap": 3}
    s.update(extra)
    return s


def test_gap_verdict_three_states_and_numbers():
    kind, text = ev.verdict_gap(_stats(10.0, 10.4), "32 Stapel × 3 Lagen")
    assert kind == "success" and text == ("32 Stapel × 3 Lagen: Die Regel „engste Passung“ kostet im Mittel 10,40 Hübe, die Zählung der Blocker 10: 4,0 % mehr. "
                                          "Das Optimum liegt dazwischen, also höchstens 4,0 % über der Untergrenze (absolut im Mittel höchstens 0,40 Hübe; in 40 von 100 Buchten trifft die Zählung "
                                          "das Optimum sicher). Die Untergrenze ist hier praktisch scharf.")
    kind, text = ev.verdict_gap(_stats(10.0, 11.5), "x")
    assert kind == "info" and text.endswith("Die Untergrenze ist hier nahe am Optimum, aber noch nicht scharf.") and "15 % mehr" in text
    kind, text = ev.verdict_gap(_stats(10.0, 14.7), "x")
    assert kind == "warning" and text.endswith("Die Lücke zwischen Untergrenze und Optimum ist hier noch groß.") and "47 % mehr" in text


def test_gap_verdict_thresholds_are_inclusive():
    assert ev.verdict_gap(_stats(100.0, 105.0), "x")[0] == "success" and C.SHARP == 0.05                    # genau 5 % zählt noch als scharf
    assert ev.verdict_gap(_stats(100.0, 105.5), "x")[0] == "info"
    assert ev.verdict_gap(_stats(100.0, 120.0), "x")[0] == "info" and C.ROUGH == 0.20                       # genau 20 % zählt noch als „nahe“
    assert ev.verdict_gap(_stats(100.0, 120.5), "x")[0] == "warning"


def _asym(rel):
    """rel: {(Stapel, Lagen): relative Lücke}; absolute Lücke und Treffer werden gesondert gesetzt."""
    return {ev.cell_key(s, l): {"rel_gap": rel(s, l), "abs_gap": 1.0, "greedy_eq_lb1": 0, "n": 200} for s in C.STACK_OPTIONS for l in (2, 3, 4, 5)}


def test_curve_verdict_three_states_and_numbers():
    asym = _asym(lambda s, l: 0.5 / s * (l - 1))                                           # 3 Lagen: unter 5 % ab 20 Stapeln -> Stufe 24
    kind, text = ev.verdict_curve(asym, 3)
    assert kind == "info" and text == "3 Lagen: Die relative Lücke fällt von 33 % bei 3 Stapeln auf 2,1 % bei 48. Höchstens 5,0 % beträgt sie ab 24 Stapeln (in dieser Stichprobe; nahe der Grenze liegt der Unterschied im Messrauschen)."
    kind, text = ev.verdict_curve(asym, 5)                                                 # 2 / s: bei 48 Stapeln 4,2 %, bei 32 6,3 %
    assert kind == "info" and "ab 48 Stapeln (in dieser Stichprobe" in text and ev.sharp_from(asym, 5) == 48
    kind, text = ev.verdict_curve(_asym(lambda s, l: 3.0 / s), 5)                         # bei 48 Stapeln 6,3 %: nie unter 5 %
    assert kind == "warning" and text == "5 Lagen: Die relative Lücke fällt von 100 % bei 3 Stapeln auf 6,3 % bei 48. Höchstens 5,0 % beträgt sie bis 48 Stapel nicht."
    kind, text = ev.verdict_curve(_asym(lambda s, l: 0.01), 2)
    assert kind == "success" and text.endswith("Höchstens 5,0 % beträgt sie schon bei 3 Stapeln.")


def test_sharp_from_requires_the_gap_to_stay_below_the_threshold():
    gaps = {3: 0.5, 4: 0.04, 5: 0.5, 6: 0.04, 8: 0.04, 10: 0.04, 12: 0.04, 16: 0.04, 24: 0.04, 32: 0.04, 48: 0.04}        # ein Ausreißer bei 5 Stapeln
    asym = {ev.cell_key(s, 2): {"rel_gap": g} for s, g in gaps.items()}
    assert ev.sharp_from(asym, 2) == 6                                                      # ab 6 Stapeln bleibt sie darunter
    assert ev.sharp_from({ev.cell_key(s, 2): {"rel_gap": 0.06 if s == 48 else 0.01} for s in C.STACK_OPTIONS}, 2) is None     # die letzte Stufe zählt


def _abs_asym(first_abs, last_abs, first_rel=0.5, last_rel=0.02, first_eq=44, last_eq=86):
    asym = {}
    for l in (2, 3, 4, 5):
        asym[ev.cell_key(3, l)] = {"rel_gap": first_rel, "abs_gap": first_abs, "greedy_eq_lb1": first_eq, "n": 200}
        asym[ev.cell_key(48, l)] = {"rel_gap": last_rel, "abs_gap": last_abs, "greedy_eq_lb1": last_eq, "n": 200}
    return asym


def test_absolute_verdict_two_states_and_numbers():
    kind, text = ev.verdict_absolute(_abs_asym(1.63, 0.75), 3)
    assert kind == "info" and text == ("3 Lagen: Die relative Lücke fällt von 50 % auf 2,0 %, die absolute von 1,63 auf 0,75 Hübe; die Zählung beweist das Optimum in 44 von 200 Buchten "
                                       "bei 3 Stapeln und in 86 bei 48. Auch die absolute Lücke schrumpft.")
    kind, text = ev.verdict_absolute(_abs_asym(8.08, 8.74, last_eq=0, first_eq=0), 5)
    assert kind == "warning" and text.endswith("Die absolute Lücke sinkt nur wenig oder bleibt (bei 48 Stapeln noch mindestens halb so groß wie bei 3): Das Verhältnis wird kleiner, weil die Untergrenze wächst, nicht weil die Lücke wesentlich schrumpft.")
    assert ev.verdict_absolute(_abs_asym(2.0, 1.0), 4)[0] == "warning" and C.ABS_KEEP == 0.5            # genau die Hälfte zählt noch als „bleibt“
    assert ev.verdict_absolute(_abs_asym(2.0, 0.99), 4)[0] == "info"


def _exact(opt_rel, greedy_rel, n=60, opt=10.0, lb1=9.0, greedy=10.1, eq=50):
    return {"exact": {"n": n, "capped": 0, "opt": opt, "lb1": lb1, "greedy": greedy, "opt_rel": opt_rel, "greedy_rel": greedy_rel, "greedy_eq_opt": eq}}


def test_exact_verdict_three_states_and_numbers():
    kind, text = ev.verdict_exact(_exact(0.033, 0.0, opt=6.2, lb1=6.0, greedy=6.2, eq=60), "12 × 2")
    assert kind == "success" and text == ("12 × 2: Das Optimum liegt im Mittel 3,3 % über der Untergrenze (Optimum 6,20, Untergrenze 6); die Regel liegt 0,0 % über dem Optimum und trifft es "
                                          "in 60 von 60 Buchten. Die Untergrenze ist hier praktisch scharf.")
    assert ev.verdict_exact(_exact(0.103, 0.008), "x")[0] == "info" and ev.verdict_exact(_exact(0.381, 0.03), "x")[0] == "warning"
    assert ev.verdict_exact(_exact(0.05, 0.0), "x")[0] == "success" and ev.verdict_exact(_exact(0.2, 0.0), "x")[0] == "info" and ev.verdict_exact(_exact(0.2001, 0.0), "x")[0] == "warning"
