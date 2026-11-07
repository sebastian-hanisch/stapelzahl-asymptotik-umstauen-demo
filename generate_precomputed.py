"""Erzeugt sza_bands.json: Kennzahlen der festen Buchten (Seeds ab 0) für drei Auswertungen.

    python generate_precomputed.py

"asym":  je Zelle (Stapel × Lagen, Platz 2, ASYM_BAYS Buchten) Mittel von LB1, LB2 und der Regel „engste Passung“, relative und absolute Lücke, Treffer der Zählung (sample_stats).
"exakt": je Zelle aus EXACT_CELLS zusätzlich das Optimum aus der Suche (EXACT_BAYS Buchten, Knotenlimit EXACT_CAP_BAND je Bucht).
"platz": je Lagenzahl, Platz (1 bis 4) und Stapelzahl die relative Lücke (ASYM_BAYS Buchten).

Rechenzeit einige Minuten (die exakten Zellen 12 × 3 und 8 × 4 sind die langsamsten; die Zellen laufen in getrennten Prozessen). Dieselben Funktionen wie die Tests
(`sza_evaluation.bay_rows`, `sample_stats`); die Datei speichert nur Kennzahlen, keine Zeilen."""

import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import sza_constants as C
import sza_evaluation as ev

sys.stdout.reconfigure(encoding="utf-8")


def job(kind, stacks, layers, extra):
    if kind == "asym":
        return kind, ev.cell_key(stacks, layers), ev.sample_stats(ev.bay_rows(stacks, layers, C.DEFAULT_EXTRA, range(C.ASYM_BAYS)))
    if kind == "exakt":
        return kind, ev.cell_key(stacks, layers), ev.sample_stats(ev.bay_rows(stacks, layers, C.DEFAULT_EXTRA, range(C.EXACT_BAYS), True, C.EXACT_CAP_BAND))
    stats = ev.sample_stats(ev.bay_rows(stacks, layers, extra, range(C.ASYM_BAYS)))
    return kind, ev.platz_key(layers, extra, stacks), stats["rel_gap"]


def main():
    tasks = [("exakt", s, l, C.DEFAULT_EXTRA) for s, l in reversed(C.EXACT_CELLS)]               # die langsamen zuerst
    tasks += [("asym", s, l, C.DEFAULT_EXTRA) for l in (5, 4, 3, 2) for s in reversed(C.STACK_OPTIONS)]
    tasks += [("platz", s, l, e) for l in C.PLATZ_LAYERS for e in (1, 2, 3, 4) for s in C.PLATZ_STACKS]
    out = {"asym": {}, "exakt": {}, "platz": {}}
    with ProcessPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) - 2)) as pool:
        futures = {pool.submit(job, *t): t for t in tasks}
        for fut in as_completed(futures):
            kind, key, stats = fut.result()
            out[kind][key] = stats
            print(kind, key, "fertig", flush=True)
    with open("sza_bands.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("geschrieben: sza_bands.json", flush=True)


if __name__ == "__main__":
    main()
