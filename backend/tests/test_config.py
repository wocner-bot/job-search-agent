from app.config import Settings


def test_render_postgresql_url_uses_installed_psycopg_driver():
    settings = Settings(database_url="postgresql://user:pass@host:5432/job_search_agent")

    assert settings.sqlalchemy_database_url == "postgresql+psycopg://user:pass@host:5432/job_search_agent"


def test_legacy_postgres_url_uses_installed_psycopg_driver():
    settings = Settings(database_url="postgres://user:pass@host:5432/job_search_agent")

    assert settings.sqlalchemy_database_url == "postgresql+psycopg://user:pass@host:5432/job_search_agent"
