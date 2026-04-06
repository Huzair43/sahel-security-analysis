from flask import Blueprint, render_template

from flask_app.utils.data_loader import load_main_data

map_bp = Blueprint("map", __name__)


@map_bp.route("/map")
def map_view():
    df = load_main_data()
    return render_template(
        "map.html",
        total_incidents=f"{len(df):,}",
    )
