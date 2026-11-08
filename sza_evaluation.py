"""Kennzahlen, Verdikt-Logik, vorberechnete Tabellen. Reine Funktionen: die App ruft st.<Art>(Text), die Tests prüfen jede Zahl und jede Schwelle."""

import json
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from statistics import mean

import sza_algorithm as A
import sza_constants as C
from sza_scenario import make_bay, max_height

BANDS_FILE = Path(__file__).resolve().parent / "sza_bands.json"


@dataclass(frozen=True)
class Settings:
    stacks: int = C.DEFAULT_STACKS
    layers: int = C.DEFAULT_LAYERS
    extra: int = C.DEFAULT_EXTRA
    bays: int = C.DEFAULT_BAYS
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    rows: tuple             # je Bucht {"seed", "lb1", "lb2", "greedy", "opt" (None: nicht gerechnet oder am Limit)}
    exact: bool             # wurde das Optimum gerechnet?
    stats: dict             # sample_stats der Zeilen
    first_bay: tuple        # die erste Bucht der Stichprobe (zur Ansicht)
    height: int


def bay_rows(stacks: int, layers: int, extra: int, seeds, exact: bool = False, cap: int = C.EXACT_CAP) -> list[dict]:
    """Je Bucht: LB1, LB2 (an der Wurzel, nach dem ersten Abruf), Kosten der Regel „engste Passung“ und, wenn verlangt, das Optimum (None am Knotenlimit)."""
    height = max_height(layers, extra)
    rows = []
    for sd in seeds:
        bay = make_bay(stacks, layers, sd)
        st = A.autopop(bay)[0]
        row = {"seed": sd, "lb1": A.lb1(st), "lb2": A.lb2(st), "greedy": A.greedy(bay, height), "opt": None}
        if exact:
            row["opt"] = A.search(bay, height, "LB2", cap).optimum
        rows.append(row)
    return rows


def sample_stats(rows: list[dict]) -> dict:
    """Kennzahlen einer Stichprobe: Mittel von LB1, LB2 und Regel, relative Lücke (Mittel der Regel / Mittel von LB1 − 1), absolute Lücke (Mittel), Zahl der Buchten,
    in denen die Regel gleich LB1 beziehungsweise LB2 ist (dann ist die Untergrenze bewiesen optimal), größte Lücke; mit Optimum die entsprechenden Größen."""
    n = len(rows)
    lb1, lb2, gr = mean(r["lb1"] for r in rows), mean(r["lb2"] for r in rows), mean(r["greedy"] for r in rows)
    out = {"n": n, "lb1": lb1, "lb2": lb2, "greedy": gr, "rel_gap": (gr / lb1 - 1) if lb1 else None, "rel_gap_lb2": (gr / lb2 - 1) if lb2 else None, "abs_gap": gr - lb1,
           "greedy_eq_lb1": sum(1 for r in rows if r["greedy"] == r["lb1"]), "greedy_eq_lb2": sum(1 for r in rows if r["greedy"] == r["lb2"]),
           "max_gap": max(r["greedy"] - r["lb1"] for r in rows)}
    solved = [r for r in rows if r["opt"] is not None]
    if solved:
        opt = mean(r["opt"] for r in solved)
        base1, basegr = mean(r["lb1"] for r in solved), mean(r["greedy"] for r in solved)
        out["exact"] = {"n": len(solved), "capped": n - len(solved), "opt": opt, "lb1": base1, "lb2": mean(r["lb2"] for r in solved), "greedy": basegr,
                        "opt_rel": (opt / base1 - 1) if base1 else None, "greedy_rel": (basegr / opt - 1) if opt else None,
                        "opt_eq_lb1": sum(1 for r in solved if r["opt"] == r["lb1"]), "opt_eq_lb2": sum(1 for r in solved if r["opt"] == r["lb2"]),
                        "greedy_eq_opt": sum(1 for r in solved if r["greedy"] == r["opt"]),
                        "violations": sum(1 for r in solved if not r["lb1"] <= r["lb2"] <= r["opt"] <= r["greedy"])}
    return out


def analyse(settings: Settings) -> Analysis:
    exact = settings.stacks * settings.layers <= C.EXACT_MAX_CONTAINERS
    rows = bay_rows(settings.stacks, settings.layers, settings.extra, range(settings.seed, settings.seed + settings.bays), exact)
    return Analysis(tuple(rows), exact, sample_stats(rows), make_bay(settings.stacks, settings.layers, settings.seed), max_height(settings.layers, settings.extra))


# ---------------------------------------------------------------- Formate

def num(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ")


def _half_up(x: float, digits: int) -> str:
    """Kaufmännisch gerundet (…5 rundet auf) und mit `digits` Nachkommastellen; vermeidet, dass 1,635 als 1,63 und 6,25 als 6,2 erscheint (binäre Gleitkommadarstellung)."""
    d = Decimal(repr(round(float(x), 9))).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return f"{d:.{digits}f}"


def dec(x: float, digits: int = 2) -> str:
    """Dezimalzahl mit Komma und Leerzeichen als Tausendertrenner; ganzzahlige Werte ohne Nachkommastellen."""
    x = round(float(x), 6)
    if x.is_integer():
        return num(int(x))
    whole, frac = _half_up(x, digits).split(".")
    return f"{num(int(whole))},{frac}"


def percent_text(x: float) -> str:
    """Anteil als Prozent: unter 10 % mit einer Nachkommastelle, sonst ganzzahlig (Komma)."""
    p = x * 100
    return (_half_up(p, 1) if p < 10 else _half_up(p, 0)).replace(".", ",") + " %"


def ratio3(x: float) -> str:
    """Relative Lücke mit drei Nachkommastellen (Komma), wie in den Tabellen."""
    return _half_up(x, 3).replace(".", ",")


# ---------------------------------------------------------------- Verdikte

def _le(x: float, limit: float) -> bool:
    """x <= limit mit Toleranz für Gleitkommarauschen (105 / 100 − 1 ist 0,05000000000000004)."""
    return round(x, 9) <= limit


def verdict_gap(stats: dict, name: str) -> tuple[str, str]:
    """Verdikt der Kernfrage für eine Stichprobe: wie weit liegt die Regel (obere Schranke des Optimums) über der Zählung der Blocker?"""
    if stats["rel_gap"] is None:
        return "info", f"{name}: Die Stichprobe hat keine Blocker (Untergrenze 0); es gibt nichts zu vergleichen."
    r = stats["rel_gap"]
    text = (f"{name}: Die Regel „engste Passung“ kostet im Mittel {dec(stats['greedy'])} Hübe, die Zählung der Blocker {dec(stats['lb1'])}: {percent_text(r)} mehr. "
            f"Das Optimum liegt dazwischen, also höchstens {percent_text(r)} über der Untergrenze (absolut im Mittel höchstens {dec(stats['abs_gap'])} Hübe; "
            f"in {stats['greedy_eq_lb1']} von {stats['n']} Buchten trifft die Zählung das Optimum sicher).")
    if _le(r, C.SHARP):
        return "success", text + " Die Untergrenze ist hier praktisch scharf."
    if _le(r, C.ROUGH):
        return "info", text + " Die Untergrenze ist hier nahe am Optimum, aber noch nicht scharf."
    return "warning", text + " Die Lücke zwischen Untergrenze und Optimum ist hier noch groß."


def exact_line(stats: dict) -> str | None:
    """Zusatzzeile mit dem gerechneten Optimum (None, wenn nicht gerechnet)."""
    e = stats.get("exact")
    if not e:
        return None
    scope = f"{e['n']} von {stats['n']} Buchten, {e['capped']} am Knotenlimit" if e["capped"] else f"{e['n']} Buchten"
    return (f"Gerechnet (Optimum aus der Suche, {scope}): Optimum im Mittel {dec(e['opt'])}, Untergrenze {dec(e['lb1'])}, Regel {dec(e['greedy'])}. "
            f"Das Optimum liegt {percent_text(e['opt_rel'])} über der Untergrenze, die Regel {percent_text(e['greedy_rel'])} über dem Optimum; "
            f"die Regel trifft das Optimum in {e['greedy_eq_opt']} von {e['n']} Buchten, die Zählung der Blocker in {e['opt_eq_lb1']}.")


def load_bands() -> dict:
    """Vorberechnete Kennzahlen, erzeugt von generate_precomputed.py: {"asym": {"s,l": sample_stats}, "exakt": {"s,l": sample_stats}, "platz": {"l,extra,s": relative Lücke}}."""
    return json.loads(BANDS_FILE.read_text(encoding="utf-8"))


def cell_key(stacks: int, layers: int) -> str:
    return f"{stacks},{layers}"


def platz_key(layers: int, extra: int, stacks: int) -> str:
    return f"{layers},{extra},{stacks}"


def sharp_from(asym: dict, layers: int):
    """Kleinste Stapelzahl der Stufen, ab der die relative Lücke höchstens SHARP beträgt und darunter bleibt; None, wenn nie."""
    result = None
    for s in reversed(C.STACK_OPTIONS):
        gap = asym[cell_key(s, layers)]["rel_gap"]
        if _le(gap, C.SHARP):
            result = s
        else:
            break
    return result


def verdict_curve(asym: dict, layers: int) -> tuple[str, str]:
    """Verdikt „ab wie vielen Stapeln ist die Untergrenze scharf?“ für eine Lagenzahl."""
    first, last = C.STACK_OPTIONS[0], C.STACK_OPTIONS[-1]
    g1, g2 = asym[cell_key(first, layers)]["rel_gap"], asym[cell_key(last, layers)]["rel_gap"]
    s = sharp_from(asym, layers)
    text = f"{layers} Lagen: Die relative Lücke fällt von {percent_text(g1)} bei {first} Stapeln auf {percent_text(g2)} bei {last}."
    if s is None:
        return "warning", text + f" Höchstens {percent_text(C.SHARP)} beträgt sie bis {last} Stapel nicht."
    if s == first:
        return "success", text + f" Höchstens {percent_text(C.SHARP)} beträgt sie schon bei {first} Stapeln."
    return "info", text + f" Höchstens {percent_text(C.SHARP)} beträgt sie ab {s} Stapeln (in dieser Stichprobe; nahe der Grenze liegt der Unterschied im Messrauschen)."


def verdict_absolute(asym: dict, layers: int) -> tuple[str, str]:
    """Verdikt „absolut gegen relativ“: schrumpft die absolute Lücke mit der Stapelzahl mit?"""
    first, last = C.STACK_OPTIONS[0], C.STACK_OPTIONS[-1]
    a, b = asym[cell_key(first, layers)], asym[cell_key(last, layers)]
    text = (f"{layers} Lagen: Die relative Lücke fällt von {percent_text(a['rel_gap'])} auf {percent_text(b['rel_gap'])}, die absolute von {dec(a['abs_gap'])} auf {dec(b['abs_gap'])} Hübe; "
            f"die Zählung beweist das Optimum in {a['greedy_eq_lb1']} von {a['n']} Buchten bei {first} Stapeln und in {b['greedy_eq_lb1']} bei {last}.")
    if b["abs_gap"] >= C.ABS_KEEP * a["abs_gap"]:
        return "warning", text + f" Die absolute Lücke sinkt nur wenig oder bleibt (bei {last} Stapeln noch mindestens halb so groß wie bei {first}): Das Verhältnis wird kleiner, weil die Untergrenze wächst, nicht weil die Lücke wesentlich schrumpft."
    return "info", text + " Auch die absolute Lücke schrumpft."


def verdict_exact(stats: dict, name: str) -> tuple[str, str]:
    """Verdikt „exakt gerechnet“ für eine Zelle."""
    e = stats["exact"]
    text = (f"{name}: Das Optimum liegt im Mittel {percent_text(e['opt_rel'])} über der Untergrenze (Optimum {dec(e['opt'])}, Untergrenze {dec(e['lb1'])}); "
            f"die Regel liegt {percent_text(e['greedy_rel'])} über dem Optimum und trifft es in {e['greedy_eq_opt']} von {e['n']} Buchten.")
    if _le(e["opt_rel"], C.SHARP):
        return "success", text + " Die Untergrenze ist hier praktisch scharf."
    if _le(e["opt_rel"], C.ROUGH):
        return "info", text + " Die Untergrenze ist hier nahe am Optimum, aber noch nicht scharf."
    return "warning", text + " Die Lücke zwischen Untergrenze und Optimum ist hier noch groß."
