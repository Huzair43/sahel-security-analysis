"""
Design system, Plotly side.

Source unique de vérité pour les couleurs de données et le rendu des figures.
Les valeurs sont le miroir exact des tokens CSS de static/css/main.css.

Usage dans une route :

    from flask_app.theme import PLOTLY_OPTS, finalize

    fig = px.bar(...)
    finalize(fig, height=340, pad="y")      # pad = axe portant les étiquettes
    html = fig.to_html(**PLOTLY_OPTS)
"""
import plotly.graph_objects as go
import plotly.io as pio

# ── Surfaces et encres (miroir des tokens CSS) ────────────────────────────────
BG        = "#0A0B0D"
SURFACE_1 = "#0F1113"
SURFACE_2 = "#141619"
SURFACE_3 = "#1B1E22"

RULE_SUBTLE = "rgba(255,255,255,0.06)"
RULE        = "rgba(255,255,255,0.10)"
RULE_STRONG = "rgba(255,255,255,0.18)"

INK_1 = "#E6E8EA"
INK_2 = "#9BA1A9"
INK_3 = "#676E77"
INK_4 = "#414751"

# ── Couleur signal, réservée à l'interaction et au haut de l'échelle ──────────
SIGNAL = "#E5484D"

# ── Familles de police (chargées par le CSS via Google Fonts) ────────────────
FONT_SANS = "IBM Plex Sans, system-ui, sans-serif"
FONT_MONO = "IBM Plex Mono, ui-monospace, monospace"

# ── Palette catégorielle, ordonnée par sévérité ──────────────────────────────
# Versant chaud : violence létale. Versant froid : troubles civils.
# Gris : catégorie résiduelle.
EVENT_COLORS = {
    "Violence against civilians": "#E5484D",
    "Battles":                    "#F2814F",
    "Explosions/Remote violence": "#EFC05B",
    "Protests":                   "#5FA8B8",
    "Riots":                      "#7C87D6",
    "Strategic developments":     "#6B7280",
}

COUNTRY_COLORS = {
    "Burkina Faso": "#E5645A",
    "Mali":         "#E9B84A",
    "Niger":        "#63A0C9",
}

# Ordre d'affichage stable, du plus létal au résiduel.
EVENT_ORDER = list(EVENT_COLORS.keys())

# ── Échelle séquentielle, monochrome ancrée sur la couleur signal ────────────
SEQUENTIAL = [
    [0.00, "#14161A"],
    [0.20, "#3A2226"],
    [0.40, "#6E2B2C"],
    [0.60, "#A83A34"],
    [0.80, "#E5484D"],
    [1.00, "#F5A87F"],
]

# Version plate, pour le JS de la carte et les color_continuous_scale.
SEQUENTIAL_FLAT = [c for _, c in SEQUENTIAL]

COLORWAY = list(EVENT_COLORS.values())

TEMPLATE_NAME = "sahel"


def _axis(mono: bool = False) -> dict:
    """Axe commun. `mono` pour les axes numériques (chiffres tabulaires)."""
    return dict(
        gridcolor=RULE_SUBTLE,
        griddash="dot",
        zerolinecolor=RULE,
        linecolor=RULE,
        showline=True,
        ticks="outside",
        ticklen=4,
        tickcolor=RULE,
        tickfont=dict(
            family=FONT_MONO if mono else FONT_SANS,
            size=11,
            color=INK_3,
        ),
        title=dict(
            font=dict(family=FONT_MONO, size=10, color=INK_4),
            standoff=12,
        ),
        automargin=True,
    )


def register() -> None:
    """Enregistre le template Plotly global et en fait le défaut."""
    pio.templates[TEMPLATE_NAME] = go.layout.Template(
        layout=go.Layout(
            font=dict(family=FONT_SANS, size=12, color=INK_2),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=COLORWAY,
            colorscale=dict(sequential=SEQUENTIAL, sequentialminus=SEQUENTIAL),
            xaxis=_axis(mono=False),
            yaxis=_axis(mono=True),
            margin=dict(l=8, r=16, t=16, b=8),
            hoverlabel=dict(
                bgcolor=SURFACE_3,
                bordercolor=RULE_STRONG,
                font=dict(family=FONT_MONO, size=11, color=INK_1),
                align="left",
            ),
            hovermode="closest",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
                font=dict(family=FONT_SANS, size=11, color=INK_2),
                title=dict(text=""),
                itemsizing="constant",
            ),
            title=dict(text=""),
            separators=".,",   # 10,086 comme dans les cartes de métriques
            bargap=0.28,
            coloraxis=dict(
                colorbar=dict(
                    outlinewidth=0,
                    thickness=8,
                    len=0.7,
                    tickfont=dict(family=FONT_MONO, size=10, color=INK_3),
                    title=dict(font=dict(family=FONT_MONO, size=10, color=INK_4)),
                )
            ),
        )
    )
    pio.templates.default = TEMPLATE_NAME


# ── Options d'export ─────────────────────────────────────────────────────────
# Plotly.js est déjà chargé dans base.html, on ne le réinjecte pas.
PLOTLY_OPTS = dict(
    full_html=False,
    include_plotlyjs=False,
    config={
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": [
            "lasso2d", "select2d", "autoScale2d",
            "hoverClosestCartesian", "hoverCompareCartesian",
            "toggleSpikelines",
        ],
        "toImageButtonOptions": {"filename": "sahel-security-analysis", "scale": 2},
    },
)


def _numeric_values(fig, axis: str):
    """Toutes les valeurs numériques portées par `axis` sur l'ensemble des traces."""
    out = []
    for trace in fig.data:
        values = getattr(trace, axis, None)
        if values is None:
            continue
        for v in values:
            try:
                out.append(float(v))
            except (TypeError, ValueError):
                continue
    return out


def pad_axis(fig, axis: str = "y", pct: float = 0.15) -> None:
    """
    Étend la plage de `axis` de `pct` au-dessus du maximum.

    Sans cela, les étiquettes de valeur placées en `textposition="outside"`
    sont dessinées en espace pixel et se font tronquer par le cadre :
    l'autorange de Plotly ne réserve qu'environ 6 %.
    """
    values = _numeric_values(fig, axis)
    if not values:
        return

    top    = max(values)
    bottom = min(values)
    if top <= 0:
        return

    floor = 0 if bottom >= 0 else bottom * (1 + pct)
    fig.update_layout({f"{axis}axis": dict(range=[floor, top * (1 + pct)])})


def bar_categories(fig, axis: str = "y", size: int = 10) -> None:
    """
    Axe de catégories d'un graphique en barres : pas de grille, pas de ticks,
    police réduite. Sur un écran étroit, des libellés de catégorie trop larges
    écrasent la zone de tracé, c'est le principal risque de lisibilité.
    """
    fig.update_layout({
        f"{axis}axis": dict(
            showgrid=False,
            showline=False,
            ticks="",
            tickfont=dict(family=FONT_SANS, size=size, color=INK_2),
        )
    })


def hide_axis(fig, axis: str = "x") -> None:
    """Axe de valeur masqué quand chaque barre porte déjà son étiquette."""
    fig.update_layout({
        f"{axis}axis": dict(
            showticklabels=False, showgrid=False, showline=False, ticks="",
            title=dict(text=""),
        )
    })


def finalize(
    fig,
    *,
    height: int | None = None,
    pad: str | None = None,
    pad_pct: float = 0.15,
    margin: dict | None = None,
    legend: bool | None = None,
    hovermode: str | None = None,
):
    """
    Applique la finition commune à toutes les figures du site.

    height     hauteur en px (utiliser l'échelle 300 / 360 / 420 / 480)
    pad        axe à étendre quand la figure porte des étiquettes de valeur
    margin     surcharge des marges, par exemple pour loger des annotations
    legend     False pour masquer la légende
    hovermode  "x unified" sur les séries temporelles
    """
    layout: dict = {}

    if height is not None:
        layout["height"] = height
    if legend is not None:
        layout["showlegend"] = legend
    if hovermode is not None:
        layout["hovermode"] = hovermode
    if margin is not None:
        layout["margin"] = margin
    if layout:
        fig.update_layout(**layout)

    # Les étiquettes ne doivent jamais être rognées par la zone de tracé.
    fig.update_traces(
        selector=dict(type="bar"),
        cliponaxis=False,
        textfont=dict(family=FONT_MONO, size=10, color=INK_2),
    )
    fig.update_traces(
        selector=dict(type="scatter"),
        textfont=dict(family=FONT_MONO, size=9, color=INK_3),
    )

    if pad:
        pad_axis(fig, axis=pad, pct=pad_pct)

    return fig
