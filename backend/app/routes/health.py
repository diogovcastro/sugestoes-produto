from flask import Blueprint, current_app
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        current_app.logger.exception("Falha ao verificar a conexão com o banco")
        return {"status": "unavailable", "database": "unavailable"}, 503

    return {"status": "ok", "database": "ok"}, 200
