
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
    from pathlib import Path

    from alembic.config import Config

    from alembic import script

    # Buscar alembic.ini relativo al repo o al directorio backend
    here = Path(__file__).resolve()
    candidates = [
        here.parents[1] / "alembic.ini",  # backend/alembic.ini
        here.parents[2] / "backend" / "alembic.ini",  # repo/backend/alembic.ini
    ]
    cfg_path = None
    for c in candidates:
        if c.exists():
            cfg_path = c
            break
    if cfg_path is None:
        raise FileNotFoundError("No se encontró alembic.ini")

    cfg = Config(str(cfg_path))
    script_dir = script.ScriptDirectory.from_config(cfg)
    assert script_dir is not None
