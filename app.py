"""Viele Stapel: wird die einfache Untergrenze scharf? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 10 der Reihe „Umstauen: Untergrenze und Suche“. Die Untergrenze aus Stück 2 zählt die Blocker. Hier die Frage, wie nah das Optimum an dieser Zahl liegt, wenn die Bucht
viele Stapel hat: Die Regel „engste Passung“ aus Stück 1 gibt eine obere Schranke, die Zählung die untere; die Demo misst, wie schnell der Abstand im Verhältnis schrumpft, und
zeigt, dass die absolute Lücke bei hohen Stapeln bleibt.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sza_constants as C
from sza_evaluation import (
    Settings,
    analyse,
    cell_key,
    dec,
    exact_line,
    load_bands,
    percent_text,
    platz_key,
    ratio3,
    verdict_absolute,
    verdict_curve,
    verdict_exact,
    verdict_gap,
)
from sza_layout import dunkles_design, kopf_css
from sza_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from sza_visualization import build_abs, build_bay, build_curve, build_exact

st.set_page_config(page_title="Viele Stapel – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _bands():
    return load_bands()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sza_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📉 Viele Stapel: wird die Untergrenze scharf?")
st.markdown(
    """
Stück 2 hat die **Untergrenze** gebaut: die Zahl der **Blocker** (Container über einem früher abzurufenden). Wie nah liegt das **Optimum** an dieser Zahl, wenn die Bucht **viele Stapel** hat? Die Regel **„engste Passung“** aus Stück 1 liefert eine **obere** Schranke des Optimums, die Zählung die **untere**: Liegen beide nah beieinander, ist das Optimum fast bekannt. Die Demo **rechnet das live** über eine Stichprobe von Buchten und misst vorberechnet, **wie schnell der Abstand im Verhältnis schrumpft**, **ob er auch absolut schrumpft** und **wie es mit dem exakt gerechneten Optimum aussieht**.

Weiter unten: die Abschnitte **🔬 Experiment** (wie schnell die Lücke schrumpft, absolut gegen relativ, exakt gerechnet, Platz), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Dies ist das zehnte Stück der Reihe „Umstauen: Untergrenze und Suche“.
"""
)

with st.expander("So wird gemessen", expanded=True):
    st.markdown(
        """
1. **Stichprobe:** *Buchten* volle Buchten mit der gewählten Zahl von Stapeln und Lagen, die Abrufnummern zufällig verteilt (feste Seeds, dieselben wie in den Stücken davor).
2. **Untergrenze (LB1):** Zahl der Blocker. **LB2** (Stück 9) zählt die Blocker ohne sicheren Stapel mit.
3. **Obere Schranke:** die **Regel „engste Passung“** arbeitet die Bucht vollständig ab; ihre Hubzahl ist mindestens das Optimum.
4. **Abstand:** Optimum − LB1 ≤ Regel − LB1. Gemessen wird der Abstand **im Verhältnis** (Mittel der Regel / Mittel von LB1 − 1) und **absolut** (Mittel der Regel − Mittel von LB1).
5. **Scharf** heißt hier: Der Abstand liegt unter **5 %**. Das ist eine Messgröße dieser Demo, kein Satz.
6. **Exakt:** Bis 24 Container (live) und bis 36 Container (vorberechnet) wird das Optimum mit der Suche aus Stück 5 und 6 gerechnet.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Stichprobe**")
    stacks = st.select_slider("Stapel", options=C.STACK_OPTIONS, key="stacks_slider", help="Wie viele Stapel die Bucht hat.")
    layers = st.slider("Lagen je Stapel", *bounds("layers_slider"), key="layers_slider", help="So viele Container stehen anfangs auf jedem Stapel.")
    extra = st.slider("Platz (Lagen über der Anfangshöhe)", *bounds("extra_slider"), key="extra_slider",
                      help="Höchsthöhe = Lagen + Platz. Standard 2. Die vorberechneten Tabellen gelten für Platz 2.")
    bays = st.select_slider("Zahl der Buchten", options=C.BAY_OPTIONS, key="bays_slider", help="So viele Buchten gehören zur Stichprobe.")
    seed = st.number_input("Erste Bucht-Nummer (Seed)", *bounds("seed_input"), key="seed_input", step=1, help="Die Stichprobe besteht aus den Buchten Nummer Seed bis Seed + Buchten − 1.")
    st.button("🎲 Neue Stichprobe würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"stacks_slider": int(stacks), "layers_slider": int(layers), "extra_slider": int(extra), "bays_slider": int(bays), "seed_input": int(seed)})

settings = Settings(int(stacks), int(layers), int(extra), int(bays), int(seed))
with st.spinner("Arbeite die Stichprobe ab (Untergrenzen, Regel" + (", exakte Suche" if settings.stacks * settings.layers <= C.EXACT_MAX_CONTAINERS else "") + ") …"):
    a = _analysis(settings)
s = a.stats

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Untergrenze LB1 (Mittel)", dec(s["lb1"]), delta=f"LB2: {dec(s['lb2'])}", delta_color="off", help="Zahl der Blocker, Mittel über die Buchten.")
m2.metric("Regel (Mittel)", dec(s["greedy"]), delta="engste Passung", delta_color="off", help="Hubzahl der Regel „engste Passung“, Mittel; eine obere Schranke des Optimums.")
m3.metric("Regel über LB1", "–" if s["rel_gap"] is None else percent_text(s["rel_gap"]), delta=f"absolut {dec(s['abs_gap'])} Hübe", delta_color="off", help="Mittel der Regel / Mittel von LB1 − 1.")
m4.metric("Zählung beweist", f"{s['greedy_eq_lb1']} von {s['n']}", delta="Regel = LB1", delta_color="off", help="Buchten, in denen die Regel die Untergrenze trifft: dann ist sie bewiesen optimal.")
if "exact" in s:
    m5.metric("Optimum (Mittel)", dec(s["exact"]["opt"]), delta=f"{s['exact']['n']} Buchten gerechnet", delta_color="off")
else:
    m5.metric("Optimum (Mittel)", "nicht gerechnet", delta=f"über {C.EXACT_MAX_CONTAINERS} Container", delta_color="off")
st.plotly_chart(build_bay(a.first_bay, a.height, target=min(c for st_ in a.first_bay for c in st_)), width="stretch", key="chart_bay")
st.caption(f"Die erste Bucht der Stichprobe (Nummer {settings.seed}). Rot: blockierende Container, grün: der nächste Abruf, grau-blau: alle übrigen.")

st.markdown("## ❓ Kernfrage: Wie weit liegt das Optimum über der Untergrenze?")
kind, text = verdict_gap(s, f"{settings.stacks} Stapel × {settings.layers} Lagen")
getattr(st, kind)(text)
line = exact_line(s)
if line:
    st.info(line)

st.markdown("---")

# --- Experiment: wie schnell schrumpft die Lücke -----------------------------------------------------------------------------------------------------

bands = _bands()
asym, exakt, platz = bands["asym"], bands["exakt"], bands["platz"]
st.subheader("🔬 Experiment: Wie schnell schrumpft die Lücke?")
st.caption(f"Relative Lücke = Mittel der Regel / Mittel von LB1 − 1; je Zelle {C.ASYM_BAYS} feste Buchten (Platz 2), vorberechnet (`generate_precomputed.py`). Das Optimum liegt höchstens so weit über der Untergrenze.")
ta = ["| Stapel | " + " | ".join(f"{l_} Lagen" for l_ in (2, 3, 4, 5)) + " |", "|---|---|---|---|---|"]
for s_ in C.STACK_OPTIONS:
    ta.append(f"| {s_} | " + " | ".join(ratio3(asym[cell_key(s_, l_)]["rel_gap"]) for l_ in (2, 3, 4, 5)) + " |")
st.markdown("\n".join(ta))
st.plotly_chart(build_curve(asym), width="stretch", key="chart_curve")
st.markdown(f"**{settings.layers} Lagen (Ihre Einstellung):**")
kind, text = verdict_curve(asym, settings.layers)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: absolut gegen relativ ------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Absolut gegen relativ")
st.caption("Absolute Lücke = Mittel der Regel − Mittel von LB1 (Hübe); in Klammern die Zahl der Buchten von 200, in denen die Zählung das Optimum sicher trifft (Regel = LB1).")
tb = ["| Stapel | " + " | ".join(f"{l_} Lagen" for l_ in (2, 3, 4, 5)) + " |", "|---|---|---|---|---|"]
for s_ in C.STACK_OPTIONS:
    tb.append(f"| {s_} | " + " | ".join(f"{dec(asym[cell_key(s_, l_)]['abs_gap'])} ({asym[cell_key(s_, l_)]['greedy_eq_lb1']})" for l_ in (2, 3, 4, 5)) + " |")
st.markdown("\n".join(tb))
st.plotly_chart(build_abs(asym), width="stretch", key="chart_abs")
st.markdown(f"**{settings.layers} Lagen (Ihre Einstellung):**")
kind, text = verdict_absolute(asym, settings.layers)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: exakt gerechnet ------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Exakt gerechnet")
st.caption(f"Das Optimum aus der Suche (Stück 5 und 6) in {len(exakt)} Zellen mit je {C.EXACT_BAYS} Buchten (Knotenlimit {dec(C.EXACT_CAP_BAND)} je Bucht), Platz 2. Mittelwerte; „Optimum = LB1“ zählt die Buchten, in denen die Zählung exakt trifft.")
tc = ["| Zelle (Buchten) | LB1 | LB2 | Optimum | Regel | Optimum = LB1 | Optimum über LB1 | Regel über Optimum | Regel = Optimum |", "|---|---|---|---|---|---|---|---|---|"]
for key in sorted(exakt, key=lambda k: (int(k.split(",")[1]), int(k.split(",")[0]))):
    e = exakt[key]["exact"]
    st_, ly_ = key.split(",")
    cap_txt = f", {e['capped']} am Limit" if e["capped"] else ""
    tc.append(f"| {st_} × {ly_} ({e['n']}{cap_txt}) | {dec(e['lb1'])} | {dec(e['lb2'])} | {dec(e['opt'])} | {dec(e['greedy'])} | {e['opt_eq_lb1']} | "
              f"{percent_text(e['opt_rel'])} | {percent_text(e['greedy_rel'])} | {e['greedy_eq_opt']} |")
st.markdown("\n".join(tc))
st.plotly_chart(build_exact(exakt), width="stretch", key="chart_exact")
here = exakt.get(cell_key(settings.stacks, settings.layers))
st.markdown(f"**Zelle {settings.stacks} × {settings.layers} (Ihre Einstellung):**")
if here is None:
    st.info(f"Für {settings.stacks} × {settings.layers} wurde das Optimum nicht vorberechnet; die Tabelle zeigt die Zellen, die gerechnet wurden.")
else:
    kind, text = verdict_exact(here, f"{settings.stacks} × {settings.layers}")
    getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: Platz --------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Platz")
st.caption("Relative Lücke (Regel / LB1 − 1) bei Platz 1 bis 4 (Höchsthöhe = Lagen + Platz), je Zelle 200 Buchten.")
td = ["| Lagen, Stapel | " + " | ".join(f"Platz {e_}" for e_ in (1, 2, 3, 4)) + " |", "|---|---|---|---|---|"]
for l_ in C.PLATZ_LAYERS:
    for s_ in C.PLATZ_STACKS:
        td.append(f"| {l_} Lagen, {s_} Stapel | " + " | ".join(ratio3(platz[platz_key(l_, e_, s_)]) for e_ in (1, 2, 3, 4)) + " |")
st.markdown("\n".join(td))
st.info("Ab Platz 2 ändert zusätzlicher Platz nur wenig (bei 3 Lagen unter 5 %, bei 4 Lagen 7 bis 8 % relativ bis Platz 4); bei Platz 1 ist die Lücke etwas größer. Die Tabellen oben gelten für Platz 2.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Messung, kein Beweis** | Die Lücke schrumpft in den Messungen im Verhältnis; belegt bis 48 Stapel und 5 Lagen. Ein Satz ist das nicht; die Aussage der Literatur (Borjian, Manshadi und Jaillet) ist aus dem Gedächtnis zugeordnet und nicht gelesen. | – |
| **Obere Schranke = Regel** | Das Optimum ist nur über die Regel von oben begrenzt; „höchstens x % über der Untergrenze“ gilt, die tatsächliche Lücke kann kleiner sein (exakt gerechnet bis 36 Container). | – |
| **Volle Buchten, restricted, Platz 2 in den Tabellen** | Teilgefüllte Buchten (kleiner Füllgrad), andere Hubmengen (Stück 3) und anderer Platz ändern die Zahlen; Platz wurde nur für 3 und 4 Lagen gemessen. | – |
| **Feste Lagenzahl** | Bei mehr Lagen schrumpft die Lücke langsamer (bei 5 Lagen und 48 Stapeln noch 6,7 %); mit wachsender Stapelhöhe wurde nicht gemessen. | – |
| **Kleine exakte Zellen** | 60 Buchten je Zelle, bei 6 × 4 und 8 × 4 je eine Bucht am Knotenlimit; die Aussagen sind grob. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben:** $S$ Stapel mit je $h$ Containern (volle Bucht), Höchsthöhe $H = h + p$ (Platz $p$), Abrufnummern $1, \dots, N$ mit $N = S\,h$ zufällig verteilt, restricted.

**Untergrenze.** $\text{LB1} = |\{c : c \text{ liegt über einem kleineren im selben Stapel}\}|$ (Stück 2). Für jede Bucht gilt $\text{LB1} \le \text{OPT}$.

**Obere Schranke.** $\text{G}$ sei die Hubzahl der Regel „engste Passung“ (Stück 1). Sie ist zulässig, also $\text{OPT} \le \text{G}$.

**Abstand.** Aus beiden folgt
$$\frac{\text{OPT}}{\text{LB1}} - 1 \;\le\; \frac{\text{G}}{\text{LB1}} - 1 =: \rho(S, h).$$
Die Demo misst $\bar\rho(S,h) = \bar G / \overline{\text{LB1}} - 1$ über feste Buchten (Mittel über die Buchten, Verhältnis der Mittel). **Die Messung:** $\bar\rho$ fällt mit $S$ bei jedem $h$ (ungefähr wie $1/S$), langsamer bei größerem $h$. Daraus folgt für die Stichprobe, dass das Optimum im Verhältnis immer näher an der Untergrenze liegt, **nicht** dass die absolute Lücke $\bar G - \overline{\text{LB1}}$ verschwindet: Sie bleibt bei $h = 5$ bei 8 bis 9 Hüben, während $\overline{\text{LB1}}$ mit $S$ wächst.

**Warum die Lücke mit $S$ sinkt (Plausibilität, kein Beweis).** Ein zweiter Hub ist sicher erzwungen, wenn jeder andere Stapel einen früheren Abruf enthält als der Blocker selbst (LB2, Stück 9). Mit mehr Stapeln wird das seltener: Ein Blocker findet eher einen Stapel mit späterem frühestem Abruf.

**Literatur.** Borjian, Manshadi und Jaillet untersuchen das Relocation-Problem mit Näherungsgarantien, Asymptotik und unvollständiger Information; die Aussage „die einfache Untergrenze wird bei vielen Stapeln asymptotisch scharf“ ist aus dem Gedächtnis zugeordnet, **nicht gelesen**. Hier wird nur gemessen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
