"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

STACK_OPTIONS = (3, 4, 5, 6, 8, 10, 12, 16, 24, 32, 48)   # Zahl der Stapel (Stufen des Reglers)
DEFAULT_STACKS = 3
LAYERS_MIN, LAYERS_MAX, DEFAULT_LAYERS = 2, 5, 3          # Anfangsfüllung je Stapel (Lagen)
EXTRA_MIN, EXTRA_MAX, DEFAULT_EXTRA = 1, 4, 2             # Platz: Höchsthöhe = Lagen + Zuschlag (Standard 2 wie in Stück 1 bis 9)
BAY_OPTIONS = (20, 50, 100, 200)                          # Zahl der Buchten einer Stichprobe (Stufen des Reglers)
DEFAULT_BAYS = 100
DEFAULT_SEED = 0                                          # erste Bucht-Nummer der Stichprobe: Seeds seed bis seed + Buchten − 1
SEED_MAX = 999999

EXACT_MAX_CONTAINERS = 24                                 # das Optimum wird live nur bis zu dieser Containerzahl gerechnet
EXACT_CAP = 100_000                                       # Knotenlimit der Suche je Bucht (live)

# Zellen der vorberechneten Tabellen. Dieselben Buchten wie in Stück 1 bis 9 (Seeds ab 0, Platz 2).
ASYM_BAYS = 200                                           # A und B: Buchten je Zelle (Stapel × Lagen)
EXACT_CELLS = ((3, 3), (4, 3), (6, 3), (8, 3), (10, 3), (12, 3), (3, 4), (4, 4), (6, 4), (8, 4), (4, 2), (8, 2), (12, 2))     # C: exakt gerechnet
EXACT_BAYS = 60
EXACT_CAP_BAND = 400_000                                  # Knotenlimit je Bucht in der Vorberechnung
PLATZ_LAYERS = (3, 4)                                     # D: Platz 1 bis 4
PLATZ_STACKS = (4, 8, 16, 32)

# Schwellen der Verdikte
SHARP = 0.05                                              # „scharf“: Regel liegt höchstens so viel (relativ) über der Untergrenze
ROUGH = 0.20                                              # „noch offen“: darüber
ABS_KEEP = 0.5                                            # „die absolute Lücke bleibt“: Lücke bei 48 Stapeln mindestens so groß wie dieser Anteil der Lücke bei 3 Stapeln

COLOR_CELL = "#7a8fa6"
COLOR_BLOCK = "#b5545a"        # blockierend (liegt über einem früher abzurufenden)
COLOR_TARGET = "#2F6B65"       # nächster Abruf
COLOR_LINES = {2: "#7a8fa6", 3: "#2F6B65", 4: "#d9822b", 5: "#4c78a8"}     # je Lagenzahl

# Sonderbuchten und Presets (Eigenschaften in tests/test_presets.py)
PRESETS = {
    "Wenige Stapel (3 Stapel, 3 Lagen)": {"stacks": 3, "layers": 3, "extra": DEFAULT_EXTRA, "bays": 100, "seed": 0},
    "Viele Stapel (32 Stapel, 3 Lagen)": {"stacks": 32, "layers": 3, "extra": DEFAULT_EXTRA, "bays": 100, "seed": 0},
    "Zwei Lagen (16 Stapel, 2 Lagen)": {"stacks": 16, "layers": 2, "extra": DEFAULT_EXTRA, "bays": 100, "seed": 0},
    "Hohe Stapel (16 Stapel, 5 Lagen)": {"stacks": 16, "layers": 5, "extra": DEFAULT_EXTRA, "bays": 100, "seed": 0},
    "Exakt: 8 Stapel, 3 Lagen": {"stacks": 8, "layers": 3, "extra": DEFAULT_EXTRA, "bays": 50, "seed": 0},
}
PRESET_HELP = {
    "Wenige Stapel (3 Stapel, 3 Lagen)": "9 Container: Die Regel kostet im Mittel rund die Hälfte mehr Hübe als die Zählung der Blocker.",
    "Viele Stapel (32 Stapel, 3 Lagen)": "96 Container: Die Regel liegt nur noch rund 3 % über der Zählung der Blocker.",
    "Zwei Lagen (16 Stapel, 2 Lagen)": "32 Container: Schon bei 16 Stapeln liegt die Regel unter 3 % über der Untergrenze.",
    "Hohe Stapel (16 Stapel, 5 Lagen)": "80 Container: Das Verhältnis schrumpft langsam, die absolute Lücke bleibt bei rund 8 Hüben, die Zählung trifft nie.",
    "Exakt: 8 Stapel, 3 Lagen": "24 Container, 50 Buchten: Das Optimum wird live gerechnet und mit der Untergrenze und der Regel verglichen.",
}
