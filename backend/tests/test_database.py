
from app.core.config import settings


def test_settings_loads():
    assert settings.APP_NAME == "ai-automation-control-center"


def test_database_url_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    import importlib

    from app.core import config

    importlib.reload(config)
    assert config.settings.DATABASE_URL == "postgresql+psycopg://test:test@localhost:5432/test"


def test_get_db_dependency():
    from app.core import database

    gen = database.get_db()
    session = next(gen)
    assert session is not None
    try:
        next(gen)
    except StopIteration:
        pass


def test_imports_without_db_connection():
    from app import main
    from app.core import config, database
    assert config.settings is not None
    assert database.Base is not None
    assert main.app is not None


def test_alembic_can_load():
    from alembic.config import Config

    from alembic import script

    cfg = Config("backend/alembic.ini")
    script_dir = script.ScriptDirectory.from_config(cfg)
    assert script_dir is not None
