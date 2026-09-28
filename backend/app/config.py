import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Config:
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def build_database_url() -> URL:
        load_dotenv()

        user = os.getenv("SUGESTOES_DB_USER")
        password = os.getenv("SUGESTOES_DB_PASSWORD")
        host = os.getenv("SUGESTOES_DB_HOST")
        port = int(os.getenv("SUGESTOES_DB_PORT"))
        db_name = os.getenv("SUGESTOES_DB_NAME")

        return URL.create(
            drivername="postgresql+psycopg",
            username=user,
            password=password,
            host=host,
            port=port,
            database=db_name,
        )