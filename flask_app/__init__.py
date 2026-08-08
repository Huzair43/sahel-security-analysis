import os

from flask import Flask
from flask_compress import Compress

compress = Compress()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"]        = os.environ.get("SECRET_KEY", os.urandom(32))
    app.config["COMPRESS_MIMETYPES"] = [
        "text/html", "application/json",
        "text/css", "application/javascript",
    ]
    app.config["COMPRESS_LEVEL"] = 6   # gzip level (1=fast, 9=max)

    compress.init_app(app)

    # ── Design system : template Plotly global ────────────────────────────────
    from flask_app.theme import register as register_theme
    register_theme()

    # ── Blueprints ────────────────────────────────────────────────────────────
    from flask_app.routes.main import main_bp
    from flask_app.routes.map import map_bp
    from flask_app.routes.trends import trends_bp
    from flask_app.routes.hotspots import hotspots_bp
    from flask_app.routes.bayesian import bayesian_bp
    from flask_app.routes.about import about_bp

    # API blueprints
    from flask_app.api.data import data_bp
    from flask_app.api.chat import chat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(trends_bp)
    app.register_blueprint(hotspots_bp)
    app.register_blueprint(bayesian_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(data_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")

    return app
