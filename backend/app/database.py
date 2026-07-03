from collections.abc import Generator

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401
from app.config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


def ensure_sqlite_schema_compatible(database_engine=engine) -> None:
    if database_engine.dialect.name != "sqlite":
        return
    if not database_engine.url.database or database_engine.url.database == ":memory:":
        return

    with database_engine.connect() as connection:
        vacancy_table_sql = connection.execute(
            text("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'vacancy'")
        ).scalar_one_or_none()

    if vacancy_table_sql is None:
        return

    normalized_table_sql = vacancy_table_sql.lower()
    has_status_constraint = (
        "application_status" in vacancy_table_sql
        and "check" in normalized_table_sql
        and "submit_status" in normalized_table_sql
    )
    if not has_status_constraint:
        raise RuntimeError(
            "Existing SQLite vacancy table is missing the application_status CHECK "
            "constraint. Remove backend/storage/job_search_agent.db or run a local "
            "database rebuild before starting the app."
        )


def init_db() -> None:
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    ensure_sqlite_schema_compatible(engine)
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
