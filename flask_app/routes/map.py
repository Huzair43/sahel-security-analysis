from flask import Blueprint, render_template

from flask_app.utils.data_loader import load_main_data

map_bp = Blueprint("map", __name__)


@map_bp.route("/map")
def map_view():
    df = load_main_data()
    event_types = sorted(df["event_type"].unique().tolist())
    total = len(df)
    return render_template(
        "map.html",
        event_types=event_types,
        total_incidents=f"{total:,}",
    )
