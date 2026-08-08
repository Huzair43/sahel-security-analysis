from flask import Blueprint, render_template

from flask_app.theme import (
    COUNTRY_COLORS,
    EVENT_COLORS,
    EVENT_ORDER,
    INK_1,
    INK_3,
    INK_4,
    SEQUENTIAL,
    SURFACE_3,
)
from flask_app.utils.data_loader import load_main_data

map_bp = Blueprint("map", __name__)


@map_bp.route("/map")
def map_view():
    df = load_main_data()

    # Les couleurs sont passées au JS depuis theme.py : une seule source de vérité.
    return render_template(
        "map.html",
        total_incidents=f"{len(df):,}",
        year_min=int(df["year"].min()),
        year_max=int(df["year"].max()),
        event_colors=EVENT_COLORS,
        # tojson trie les clés : l'ordre de sévérité doit être passé à part.
        event_order=EVENT_ORDER,
        country_colors=COUNTRY_COLORS,
        map_theme={
            "ink1": INK_1,
            "ink3": INK_3,
            "ink4": INK_4,
            "surface3": SURFACE_3,
            "sequential": SEQUENTIAL,
        },
    )
