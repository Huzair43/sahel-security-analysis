import plotly.express as px
from flask import Blueprint, render_template

from flask_app.theme import PLOTLY_OPTS, bar_categories, finalize, hide_axis
from flask_app.utils.data_loader import (
    COUNTRY_COLORS,
    EVENT_COLORS,
    load_main_data,
    load_monthly_by_country,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    df      = load_main_data()
    monthly = load_monthly_by_country()

    # ── KPIs ─────────────────────────────────────────────────────────────────
    most_affected  = df.groupby("country")["event_id_cnty"].count().idxmax()
    deadliest_type = df.groupby("event_type")["fatalities"].sum().idxmax()

    kpis = {
        "total_incidents":  f"{len(df):,}",
        "total_fatalities": f"{df['fatalities'].sum():,}",
        "locations":        f"{df['location'].nunique():,}",
        "most_affected":    most_affected,
        "deadliest_type":   deadliest_type,
    }

    period = (
        f"{df['event_date'].min():%b %Y} : {df['event_date'].max():%b %Y}"
    )

    # ── Chart 1 : incidents par pays ─────────────────────────────────────────
    by_country = (
        df.groupby("country")
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .reset_index()
        .sort_values("incidents", ascending=False)
    )
    by_country["label"] = by_country["incidents"].map("{:,}".format)

    fig1 = px.bar(
        by_country, x="country", y="incidents",
        color="country", color_discrete_map=COUNTRY_COLORS,
        text="label",
        custom_data=["fatalities"],
        labels={"incidents": "Incidents", "country": ""},
    )
    fig1.update_traces(
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Incidents %{y:,}<br>Fatalities %{customdata[0]:,}<extra></extra>",
    )
    # pad="y" : sans cette marge, l'étiquette de la barre la plus haute
    # (Burkina Faso) est tronquée par le haut du cadre.
    # Même hauteur que le graphique voisin : les deux cartes de la rangée
    # sont étirées à la même taille par la grille.
    finalize(fig1, height=340, pad="y", legend=False,
             margin=dict(l=8, r=8, t=8, b=8))
    # Trois catégories seulement : des barres fines allègent le bloc.
    fig1.update_layout(bargap=0.55)
    chart_country = fig1.to_html(**PLOTLY_OPTS)

    # ── Chart 2 : répartition par type d'événement ───────────────────────────
    # Barres horizontales triées plutôt qu'un camembert : 6 catégories dont une
    # à 1,5 % et trois autour de 23 %, indistinguables sur des angles.
    # Tri décroissant : la catégorie dominante se lit en premier, en haut.
    by_type = (
        df.groupby("event_type")["event_id_cnty"]
        .count().reset_index(name="incidents")
        .sort_values("incidents", ascending=False)
    )
    total = by_type["incidents"].sum()
    by_type["share"] = by_type["incidents"] / total * 100
    # Étiquette courte : le compte exact reste dans le survol et dans le tableau.
    # Une étiquette longue réserve trop de marge et écrase les barres sur mobile.
    by_type["label"] = by_type["share"].map("{:.1f}%".format)

    fig2 = px.bar(
        by_type, x="incidents", y="event_type",
        orientation="h",
        color="event_type", color_discrete_map=EVENT_COLORS,
        text="label",
        custom_data=["share"],
        labels={"incidents": "Incidents", "event_type": ""},
    )
    fig2.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:,} incidents<br>%{customdata[0]:.2f}% of total<extra></extra>",
    )
    # Marge droite réservée aux étiquettes : avec cliponaxis=False elles se
    # dessinent dans la marge, hors de la zone de tracé, sans être rognées.
    finalize(fig2, height=340, pad="x", pad_pct=0.02, legend=False,
             margin=dict(l=8, r=48, t=8, b=8))
    bar_categories(fig2, axis="y")
    hide_axis(fig2, axis="x")
    chart_type = fig2.to_html(**PLOTLY_OPTS)

    # ── Chart 3 : évolution mensuelle par pays ───────────────────────────────
    fig3 = px.line(
        monthly, x="year_month_dt", y="incidents",
        color="country", color_discrete_map=COUNTRY_COLORS,
        labels={"year_month_dt": "", "incidents": "Incidents", "country": ""},
    )
    fig3.update_traces(line=dict(width=1.6), hovertemplate="%{y:,}")
    finalize(fig3, height=340, hovermode="x unified",
             margin=dict(l=8, r=8, t=32, b=8))
    chart_monthly = fig3.to_html(**PLOTLY_OPTS)

    # ── Échantillon de données brutes ────────────────────────────────────────
    raw_cols = ["event_date", "country", "admin1", "location", "event_type", "fatalities"]
    raw_data = (
        df.sort_values("event_date", ascending=False)
        .head(50)[raw_cols]
        .assign(event_date=lambda d: d["event_date"].dt.strftime("%Y-%m-%d"))
        .to_dict(orient="records")
    )

    return render_template(
        "overview.html",
        kpis=kpis,
        period=period,
        n_incidents=f"{len(df):,}",
        n_countries=by_country.shape[0],
        n_types=by_type.shape[0],
        chart_country=chart_country,
        chart_type=chart_type,
        chart_monthly=chart_monthly,
        raw_data=raw_data,
        event_colors=EVENT_COLORS,
    )
