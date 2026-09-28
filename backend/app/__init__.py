from flask import Flask

from .extensions import db, migrate
from .config import Config
from .routes.health import health_bp

def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = Config.build_database_url()

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(health_bp)

    return app
