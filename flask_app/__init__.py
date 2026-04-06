from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-key-change-in-production"

    # ── Blueprints ────────────────────────────────────────────────────────────
    from flask_app.routes.main import main_bp
    from flask_app.routes.map import map_bp
    from flask_app.routes.trends import trends_bp
    from flask_app.routes.hotspots import hotspots_bp
    from flask_app.routes.bayesian import bayesian_bp
    from flask_app.routes.about import about_bp

    # API blueprints
    from flask_app.api.data import data_bp
    from flask_app.api.chat import chat_bp  # chatbot — intégration à venir

    app.register_blueprint(main_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(trends_bp)
    app.register_blueprint(hotspots_bp)
    app.register_blueprint(bayesian_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(data_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")

    return app
