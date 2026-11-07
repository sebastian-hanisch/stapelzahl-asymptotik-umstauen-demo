"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import sza_algorithm as A
import sza_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def blocker_cells(stacks) -> set:
    """Container, die über einem früher abzurufenden im selben Stapel liegen (Position (Stapel, Lage))."""
    out = set()
    for i, s in enumerate(stacks):
        lowest = A.INF
        for j, c in enumerate(s):
            if c > lowest:
                out.add((i, j))
            else:
                lowest = c
    return out


def build_bay(stacks, height, target=None):
    """Die Bucht als Säulen: je Lage ein Balken mit der Abrufnummer. Rot: blockiert einen früher abzurufenden, grün: nächster Abruf
    (`target`, eine Abrufnummer oder None), grau-blau: übrige."""
    blockers = blocker_cells(stacks)
    fig = go.Figure()
    xs = list(range(len(stacks)))
    for j in range(height):
        ys, colors, texts = [], [], []
        for i, s in enumerate(stacks):
            if j < len(s):
                c = s[j]
                ys.append(1)
                texts.append(str(c))
                colors.append(C.COLOR_TARGET if c == target else C.COLOR_BLOCK if (i, j) in blockers else C.COLOR_CELL)
            else:
                ys.append(0)
                texts.append("")
                colors.append(C.COLOR_CELL)
        fig.add_trace(go.Bar(x=xs, y=ys, base=j, marker_color=colors, text=texts, textposition="inside", insidetextanchor="middle",
                             textfont=dict(color="#ffffff", size=16), width=0.78, showlegend=False,
                             hovertemplate="Abruf %{text}<extra></extra>", marker_line=dict(width=0)))
    fig.update_layout(barmode="overlay")
    fig.add_hline(y=height, line_dash="dot", line_color="rgba(128,128,128,0.7)", annotation_text="Höchsthöhe", annotation_position="top left")
    fig.update_xaxes(tickvals=xs, ticktext=[f"Stapel {i + 1}" for i in xs], showgrid=False)
    fig.update_yaxes(range=[0, height + 0.35], showticklabels=False, showgrid=False, zeroline=False)
    return _base(fig, height=48 * height + 90)


def build_curve(asym):
    """Relative Lücke (Regel / Untergrenze − 1, Prozent) gegen die Stapelzahl, je Lagenzahl eine Linie; beide Achsen logarithmisch, die Schwelle „scharf“ als eigene Linie. `asym`: {"s,l": sample_stats}."""
    fig = go.Figure()
    for layers in (2, 3, 4, 5):
        xs = list(C.STACK_OPTIONS)
        fig.add_trace(go.Scatter(x=xs, y=[100.0 * asym[f"{s},{layers}"]["rel_gap"] for s in xs], mode="lines+markers", name=f"{layers} Lagen", line=dict(color=C.COLOR_LINES[layers]),
                                 hovertemplate="%{x} Stapel: %{y:.1f} %<extra>%{fullData.name}</extra>"))
    fig.add_trace(go.Scatter(x=[C.STACK_OPTIONS[0], C.STACK_OPTIONS[-1]], y=[100.0 * C.SHARP] * 2, mode="lines", name="Schwelle „scharf“", line=dict(color="rgba(128,128,128,0.8)", dash="dot"),
                             hoverinfo="skip"))
    fig.update_xaxes(type="log", title_text="Zahl der Stapel (logarithmisch)", tickvals=list(C.STACK_OPTIONS), ticktext=[str(s) for s in C.STACK_OPTIONS])
    fig.update_yaxes(type="log", title_text="Regel über der Untergrenze (%, logarithmisch)")
    return _base(fig, height=380)


def build_abs(asym):
    """Absolute Lücke (Mittel der Regel − Mittel der Untergrenze, Hübe) gegen die Stapelzahl, je Lagenzahl eine Linie. `asym`: {"s,l": sample_stats}."""
    fig = go.Figure()
    for layers in (2, 3, 4, 5):
        xs = list(C.STACK_OPTIONS)
        fig.add_trace(go.Scatter(x=xs, y=[asym[f"{s},{layers}"]["abs_gap"] for s in xs], mode="lines+markers", name=f"{layers} Lagen", line=dict(color=C.COLOR_LINES[layers]),
                                 hovertemplate="%{x} Stapel: %{y:.2f} Hübe<extra>%{fullData.name}</extra>"))
    fig.update_xaxes(type="log", title_text="Zahl der Stapel (logarithmisch)", tickvals=list(C.STACK_OPTIONS), ticktext=[str(s) for s in C.STACK_OPTIONS])
    fig.update_yaxes(title_text="Regel minus Untergrenze (Hübe, Mittel)", rangemode="tozero")
    return _base(fig, height=340)


def build_exact(cells):
    """Optimum über der Untergrenze (Prozent) und Regel über dem Optimum (Prozent) je exakt gerechneter Zelle, nach Lagen und Stapeln geordnet. `cells`: {"s,l": sample_stats mit "exact"}."""
    keys = sorted(cells, key=lambda k: (int(k.split(",")[1]), int(k.split(",")[0])))
    x = [f"{k.split(',')[0]} × {k.split(',')[1]}" for k in keys]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=[100.0 * cells[k]["exact"]["opt_rel"] for k in keys], name="Optimum über der Untergrenze", marker_color=C.COLOR_LINES[3],
                         hovertemplate="%{x}: %{y:.1f} %<extra>%{fullData.name}</extra>"))
    fig.add_trace(go.Bar(x=x, y=[100.0 * cells[k]["exact"]["greedy_rel"] for k in keys], name="Regel über dem Optimum", marker_color=C.COLOR_LINES[4],
                         hovertemplate="%{x}: %{y:.1f} %<extra>%{fullData.name}</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Zelle (Stapel × Lagen)")
    fig.update_yaxes(title_text="Abstand (%)", rangemode="tozero")
    return _base(fig, height=340)
