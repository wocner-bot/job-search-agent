from collections.abc import Generator

from sqlalchemy import inspect, text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401
from app.config import get_settings


settings = get_settings()
database_url = settings.sqlalchemy_database_url
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine_kwargs = {"connect_args": connect_args}
if database_url == "sqlite:///:memory:":
    engine_kwargs["poolclass"] = StaticPool
engine = create_engine(database_url, **engine_kwargs)


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


def ensure_vacancy_columns(database_engine=engine) -> None:
    inspector = inspect(database_engine)
    if "vacancy" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("vacancy")}
    required_columns = {
        "description_raw": "VARCHAR NOT NULL DEFAULT ''",
        "requirements": "VARCHAR NOT NULL DEFAULT ''",
        "responsibilities": "VARCHAR NOT NULL DEFAULT ''",
        "vacancy_keywords": "VARCHAR NOT NULL DEFAULT ''",
    }
    missing = [name for name in required_columns if name not in existing_columns]
    if not missing:
        return
    with database_engine.begin() as connection:
        for column_name in missing:
            connection.execute(text(f"ALTER TABLE vacancy ADD COLUMN {column_name} {required_columns[column_name]}"))


def init_db() -> None:
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    ensure_sqlite_schema_compatible(engine)
    SQLModel.metadata.create_all(engine)
    ensure_vacancy_columns(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
