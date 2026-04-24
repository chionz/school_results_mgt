import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

metadata = MetaData()
Base = declarative_base()


def build_database_url(test_mode: bool = False) -> str:
    if test_mode:
        return f"sqlite:///{BASE_DIR / 'test.db'}"

    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    if db_type == "sqlite":
        sqlite_path = os.getenv("SQLITE_PATH", str(BASE_DIR / "results.db"))
        return f"sqlite:///{sqlite_path}"

    return os.getenv("DB_URL", f"sqlite:///{BASE_DIR / 'results.db'}")


def get_db_engine(test_mode: bool = False):
    database_url = build_database_url(test_mode=test_mode)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)


import app.models


def create_database():
    return Base.metadata.create_all(bind=engine)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()
