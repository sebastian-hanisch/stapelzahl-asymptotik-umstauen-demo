# Viele Stapel: wird die Untergrenze scharf? – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-stapelzahl-asymptotik-umstauen-demo.streamlit.app/)**

Zehntes Stück der Konzepte-Reihe **„Umstauen: Untergrenze und Suche“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. [Stück 2](https://sebastianhanisch-untergrenze-umstauen-demo.streamlit.app/) hat die **Untergrenze** gebaut: die Zahl der **Blocker** (Container über einem früher abzurufenden). Wie nah liegt das **Optimum** an dieser Zahl, wenn die Bucht **viele Stapel** hat? Die Regel „engste Passung“ aus [Stück 1](https://sebastianhanisch-umstauen-regeln-demo.streamlit.app/) liefert eine **obere** Schranke des Optimums, die Zählung die **untere**. Die Demo **rechnet das live** über eine Stichprobe von Buchten und misst vorberechnet, **wie schnell der Abstand im Verhältnis schrumpft**, **ob er auch absolut schrumpft** und **wie es mit dem exakt gerechneten Optimum aussieht**.

## Warum dieses Problem

Eine Untergrenze ist nur nützlich, wenn sie das Optimum nahe trifft. Bei wenigen Stapeln tut sie das nicht (bei 3 Stapeln und 3 Lagen kostet die Regel im Mittel 47 % mehr Hübe als die Zählung). Mit mehr Stapeln findet ein Blocker eher einen Stapel mit späterem frühestem Abruf und braucht seltener einen zusätzlichen Hub: Die **relative** Lücke schrumpft (3 Lagen: 3 % bei 24, 1,4 % bei 48 Stapeln). Das passt zur Aussage der Literatur (Borjian, Manshadi und Jaillet: das Optimum nähert sich bei wachsender Stapelzahl einer einfachen Untergrenze; aus dem Gedächtnis zugeordnet, **nicht gelesen**), hier nur für die Regel als obere Schranke bei fester Lagenzahl **nachgemessen**. Aber: Das gilt für das **Verhältnis**, nicht für die **absolute** Lücke. Bei 5 Lagen bleibt sie bei rund 8 Hüben, und die Zählung beweist das Optimum dort in fast **keiner** Bucht (2 von 2 200 in den Tabellen). Wie schnell die Lücke schrumpft, hängt stark von den Lagen ab.

## Methode

- **Stichprobe:** volle Buchten mit der gewählten Zahl von Stapeln und Lagen (Platz 2 in den Tabellen), die Abrufnummern zufällig, feste Seeds ab 0 (dieselben Buchten wie in den Stücken davor).
- **Untergrenze:** LB1 = Zahl der Blocker (Stück 2); LB2 (Stück 9) zählt die Blocker ohne sicheren Stapel mit.
- **Obere Schranke:** die Kosten der Regel „engste Passung“ (Stück 1) an derselben Bucht; ihre Hubzahl ist mindestens das Optimum. Also gilt Optimum / LB1 − 1 ≤ Regel / LB1 − 1.
- **Maße:** relative Lücke = Mittel der Regel / Mittel von LB1 − 1; absolute Lücke = Mittel der Regel − Mittel von LB1; Zahl der Buchten, in denen die Regel gleich LB1 ist (dann ist die Zählung bewiesen optimal).
- **Scharf** heißt in dieser Demo: höchstens 5 % (eine Messgröße, kein Satz). Verdikt in drei Zuständen: scharf (≤ 5 %), nahe (≤ 20 %), noch offen.
- **Exakt:** Das Optimum aus der Suche (Stück 5 und 6) live bis 24 Container, vorberechnet bis 36 (60 Buchten je Zelle).
- **Live:** Stichprobe aus den Reglern (Stapel 3 bis 48, Lagen 2 bis 5, Platz 1 bis 4, 20 bis 200 Buchten, erste Bucht-Nummer). **Vorberechnet** (`sza_bands.json`, `generate_precomputed.py`, einige Minuten): 44 Zellen für die relative und absolute Lücke, 13 exakte Zellen, 32 Platz-Zellen.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an festen Buchten, nachgerechnet in `tests/test_claims.py` und `tests/test_oracle_stapelzahl_asymptotik_umstauen.py`.

**A: Wie schnell schrumpft die Lücke?** (relative Lücke = Regel / Untergrenze − 1, je Zelle 200 Buchten, Platz 2)

| Stapel | 2 Lagen | 3 Lagen | 4 Lagen | 5 Lagen |
|---|---|---|---|---|
| 3 | 0,240 | 0,473 | 0,730 | 0,978 |
| 4 | 0,187 | 0,312 | 0,474 | 0,728 |
| 5 | 0,144 | 0,216 | 0,391 | 0,551 |
| 6 | 0,109 | 0,178 | 0,319 | 0,433 |
| 8 | 0,065 | 0,139 | 0,219 | 0,343 |
| 10 | 0,044 | 0,101 | 0,185 | 0,272 |
| 12 | 0,043 | 0,081 | 0,142 | 0,241 |
| 16 | 0,027 | 0,051 | 0,110 | 0,187 |
| 24 | 0,015 | 0,031 | 0,075 | 0,134 |
| 32 | 0,009 | 0,024 | 0,049 | 0,097 |
| 48 | 0,006 | 0,014 | 0,033 | 0,067 |

Die Lücke fällt bei jeder Lagenzahl über die Stufen (in den gespeicherten Zahlen streng monoton; zwischen 10 und 12 Stapeln bei 2 Lagen, 0,044 gegen 0,043, liegt der Unterschied im Rauschen) und wächst mit den Lagen. **Höchstens 5 %** beträgt sie in diesen Buchten bei 2 Lagen ab **10** Stapeln, bei 3 Lagen ab **24**, bei 4 Lagen um **32** Stapel herum (4,9 %; die 5-%-Grenze liegt dort im Messrauschen), bei 5 Lagen **bis 48 Stapel nicht**. Zwischen 8 und 48 Stapeln fällt sie ungefähr umgekehrt proportional zur Stapelzahl (Steigung im doppeltlogarithmischen Bild rund −1,4 bei 2 Lagen, −1,3 bei 3, −1,1 bei 4, −0,9 bei 5).

**B: Absolut gegen relativ** (absolute Lücke = Regel − Untergrenze in Hüben, in Klammern die Zahl der Buchten von 200, in denen die Zählung das Optimum sicher trifft)

| Stapel | 2 Lagen | 3 Lagen | 4 Lagen | 5 Lagen |
|---|---|---|---|---|
| 3 | 0,36 (133) | 1,64 (44) | 4,20 (3) | 8,08 (0) |
| 4 | 0,37 (126) | 1,45 (43) | 3,64 (8) | 7,84 (0) |
| 5 | 0,37 (126) | 1,25 (53) | 3,71 (8) | 7,50 (1) |
| 6 | 0,34 (133) | 1,24 (48) | 3,63 (4) | 7,10 (0) |
| 8 | 0,26 (148) | 1,29 (49) | 3,36 (6) | 7,37 (0) |
| 10 | 0,21 (158) | 1,16 (61) | 3,51 (7) | 7,41 (0) |
| 12 | 0,25 (150) | 1,13 (55) | 3,28 (7) | 7,92 (0) |
| 16 | 0,22 (156) | 0,95 (70) | 3,41 (16) | 8,22 (0) |
| 24 | 0,18 (165) | 0,88 (86) | 3,46 (14) | 8,73 (1) |
| 32 | 0,14 (172) | 0,91 (82) | 3,04 (16) | 8,46 (0) |
| 48 | 0,13 (174) | 0,76 (86) | 3,01 (21) | 8,75 (0) |

Bei 2 und 3 Lagen schrumpft auch die absolute Lücke (bei 3 Lagen von 1,64 auf 0,76 Hübe) und der Anteil der Buchten, in denen die Zählung das Optimum beweist, wächst (3 Lagen: 22 % auf 43 %, 2 Lagen: 67 % auf 87 %). Bei **5 Lagen bleibt sie** (8,08 auf 8,75), bei 4 Lagen sinkt sie nur von 4,20 auf 3,01 Hübe: Das Verhältnis wird kleiner, weil die Untergrenze mit der Stapelzahl wächst, nicht weil die Lücke wesentlich schrumpft.

**C: Exakt gerechnet** (60 Buchten je Zelle, Optimum aus der Suche mit LB2, Knotenlimit 400 000; Mittelwerte)

| Zelle (Buchten) | LB1 | LB2 | Optimum | Regel | Optimum = LB1 | Optimum über LB1 | Regel über Optimum | Regel = Optimum |
|---|---|---|---|---|---|---|---|---|
| 4 × 2 (60) | 1,92 | 2,20 | 2,20 | 2,20 | 43 | 15 % | 0,0 % | 60 |
| 8 × 2 (60) | 3,90 | 4,10 | 4,10 | 4,10 | 48 | 5,1 % | 0,0 % | 60 |
| 12 × 2 (60) | 6 | 6,20 | 6,20 | 6,20 | 48 | 3,3 % | 0,0 % | 60 |
| 3 × 3 (60) | 3,58 | 4,35 | 4,95 | 5,10 | 16 | 38 % | 3,0 % | 53 |
| 4 × 3 (60) | 4,43 | 5,18 | 5,68 | 5,78 | 14 | 28 % | 1,8 % | 55 |
| 6 × 3 (60) | 6,92 | 7,60 | 8,07 | 8,12 | 16 | 17 % | 0,6 % | 57 |
| 8 × 3 (60) | 9,27 | 9,90 | 10,57 | 10,62 | 15 | 14 % | 0,5 % | 57 |
| 10 × 3 (60) | 11,37 | 11,93 | 12,53 | 12,63 | 15 | 10 % | 0,8 % | 54 |
| 12 × 3 (60) | 13,92 | 14,40 | 14,97 | 15,02 | 22 | 7,5 % | 0,3 % | 57 |
| 3 × 4 (60) | 5,58 | 6,88 | 8,77 | 9,32 | 1 | 57 % | 6,3 % | 41 |
| 4 × 4 (60) | 7,22 | 8,63 | 10,13 | 11,08 | 4 | 40 % | 9,4 % | 27 |
| 6 × 4 (59, 1 am Limit) | 11,36 | 12,44 | 14,42 | 14,80 | 1 | 27 % | 2,6 % | 41 |
| 8 × 4 (59, 1 am Limit) | 15,22 | 15,95 | 17,92 | 18,27 | 2 | 18 % | 2,0 % | 44 |

Auch das **exakte** Verhältnis Optimum / LB1 − 1 fällt mit der Stapelzahl (3 Lagen: 38 % bei 3, 7,5 % bei 12 Stapeln; 4 Lagen: 57 % bei 3, 18 % bei 8). Im Mittel liegt die Regel in diesen 13 Zellen höchstens 9,4 % über dem Optimum (4 × 4); bei 2 Lagen traf sie in allen 180 gerechneten Buchten das Optimum. In keiner Bucht liegt eine Schranke außerhalb von LB1 ≤ LB2 ≤ Optimum ≤ Regel.

**D: Platz** (relative Lücke bei Platz 1 bis 4, je Zelle 200 Buchten)

| Zelle | Platz 1 | Platz 2 | Platz 3 | Platz 4 |
|---|---|---|---|---|
| 3 Lagen, 4 Stapel | 0,343 | 0,312 | 0,306 | 0,306 |
| 3 Lagen, 8 Stapel | 0,157 | 0,139 | 0,136 | 0,136 |
| 3 Lagen, 16 Stapel | 0,055 | 0,051 | 0,050 | 0,050 |
| 3 Lagen, 32 Stapel | 0,027 | 0,024 | 0,024 | 0,024 |
| 4 Lagen, 4 Stapel | 0,556 | 0,474 | 0,460 | 0,455 |
| 4 Lagen, 8 Stapel | 0,256 | 0,219 | 0,209 | 0,205 |
| 4 Lagen, 16 Stapel | 0,127 | 0,110 | 0,104 | 0,101 |
| 4 Lagen, 32 Stapel | 0,059 | 0,049 | 0,047 | 0,046 |

Ab Platz 2 ändert zusätzlicher Platz nur wenig (bei 3 Lagen unter 5 %, bei 4 Lagen 7 bis 8 % relativ bis Platz 4); bei Platz 1 ist die Lücke etwas größer.

| Frage | Befund |
|---|---|
| **Wird die Untergrenze bei vielen Stapeln scharf?** | Im Verhältnis ja: Die relative Lücke fällt von 24 bis 98 % bei 3 Stapeln auf 0,6 bis 6,7 % bei 48. Wie schnell, hängt an den Lagen: höchstens 5 % ab 10 Stapeln (2 Lagen), 24 (3), um 32 (4; die Grenze liegt dort im Messrauschen), bis 48 nicht (5). |
| **Und absolut?** | Nur bei 2 und 3 Lagen. Bei 4 Lagen sinkt die absolute Lücke nur langsam (rund 3 bis 4 Hübe), bei 5 Lagen bleibt sie bei 7 bis 9; die Zählung beweist das Optimum bei 5 Lagen in fast keiner Bucht (zwei Ausnahmen: je 1 von 200 bei 5 und bei 24 Stapeln). |
| **Stimmt das auch für das exakte Optimum?** | Ja, soweit gerechnet (bis 36 Container): Optimum über Untergrenze fällt mit der Stapelzahl, die Regel liegt im Mittel höchstens 9,4 % über dem Optimum (13 Zellen). |
| **Hilft mehr Platz?** | Wenig: ab Platz 2 bei 3 Lagen unter 5 %, bei 4 Lagen 7 bis 8 % relativ bis Platz 4. |

**Presets** (Eigenschaften in `tests/test_presets.py`): „Wenige Stapel“ (3 × 3: Regel 47 % über LB1), „Viele Stapel“ (32 × 3: 2,6 %), „Zwei Lagen“ (16 × 2: 2,5 %, die Zählung beweist das Optimum in 80 von 100 Buchten), „Hohe Stapel“ (16 × 5: 18 % und 8 Hübe absolut, kein Beweis), „Exakt: 8 Stapel, 3 Lagen“ (50 Buchten, Optimum live).

## Ehrliche Grenzen

- **Messung, kein Beweis.** Die Lücke schrumpft in den Messungen im Verhältnis, belegt bis 48 Stapel und 5 Lagen; die Aussage der Literatur ist aus dem Gedächtnis zugeordnet und nicht gelesen.
- **Obere Schranke = Regel.** „Höchstens x % über der Untergrenze“ gilt; die tatsächliche Lücke kann kleiner sein. Exakt gerechnet nur bis 36 Container (60 Buchten je Zelle, bei 6 × 4 und 8 × 4 je eine Bucht am Knotenlimit).
- **Volle Buchten, restricted, Platz 2** in den Tabellen; teilgefüllte Buchten (kleiner Füllgrad, wie sie die Literatur betrachtet) und andere Hubmengen sind nicht gemessen; Platz wurde nur für 3 und 4 Lagen gemessen.
- **Feste Lagenzahl.** Bei mehr Lagen schrumpft die Lücke langsamer (5 Lagen, 48 Stapel: 6,7 %); mit wachsender Stapelhöhe wurde nicht gemessen.
- **Verhältnis der Mittel,** nicht Mittel der Verhältnisse; bei kleinen Stichproben (20 Buchten) schwanken die Zahlen.

## Verifikation

- **Kern:** Zustände von Hand, LB1 und LB2 an Handbuchten (Hand-Bucht, Gegenbeispiel aus Stück 1), die Regel von Hand (Hand-Bucht 4 Hübe = Optimum, Gegenbeispiel 5 gegen 4), Platzmangel, Zielreihenfolge, Knotenlimit.
- **Orakel:** Optimum gegen eine **eigene Rekursion über alle Platzierungen** (ohne Untergrenze, ohne IDA\*) in allen 120 Buchten 3 × 2; die Regel gegen eine **zweite Umsetzung** (Auswahl über min()) in über 300 Buchten bis 32 Stapel; LB1 ≤ LB2 ≤ Optimum ≤ Regel in allen 3 × 2-Buchten und in Stichproben; Kernmessung in klein (die Lücke fällt von 3 über 8 auf 24 Stapel).
- **Zahlen im README:** jede Zahl der Befunde in `tests/test_claims.py` (gespeicherte Bänder, streng monoton in jeder Lagenzahl, Stufen „ab 10, 24, 32, nie“); drei Zellen, eine exakte Zelle und eine Platz-Zelle werden frisch nachgerechnet.
- **Verdikte:** reine Funktionen, jede Schwelle (5 % und 20 % einschließlich, Rundungsrauschen bei 105 / 100 − 1, Hälfte der absoluten Lücke) und jede genannte Zahl an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), Inhalt (Kennzahlen, Tabellenzeilen, Verdikte), Layout, Footer, Laufzeit-Importe, Abbildungen (Farben, gesperrte Achsen, logarithmische Achsen ohne `add_hline`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App (Aufbau nach DEMO-PLAYBOOK §2) |
| `generate_precomputed.py` | erzeugt `sza_bands.json` (Lücke, exakt, Platz) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt): streamlit, plotly |
| `sza_algorithm.py` | LB1, LB2, die Regel „engste Passung“ und die exakte Suche |
| `sza_bands.json` | vorberechnete Kennzahlen der festen Buchten je Zelle |
| `sza_constants.py` | Regler-Stufen, Limits, Zellen, Schwellen, Farben, Presets |
| `sza_evaluation.py` | Stichprobe, Kennzahlen, Verdikte (reine Funktionen) |
| `sza_layout.py` | Fester Kopf (Stylesheet) |
| `sza_presets.py` | Permalink (auf Stufen gerückt), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `sza_scenario.py` | Buchten (volle Buchten, Zufallsbuchten) |
| `sza_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handrechnung, Orakel, Randfälle, Behauptungen, Verdikte, Presets, Abbildungen, AppTest, Layout, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Ein Beweis** der Asymptotik und die Quelle (Borjian u. a.) im Volltext.
- **Teilgefüllte Buchten** (Füllgrad) und unrestricted.
- **PDF-Export:** nicht vorgesehen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

89 Tests, rund zwei Minuten.

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
