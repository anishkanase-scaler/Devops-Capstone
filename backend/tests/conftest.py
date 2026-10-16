from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

from app.config import settings
from app.db import engine
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def alembic_config():
    # Built in code (no alembic.ini) so Alembic doesn't reset pytest's logging.
    # alembic/env.py reads the database URL from app.config.settings, i.e. DATABASE_URL from pytest.ini.
    config = Config()
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


@pytest.fixture(scope="session", autouse=True)
def migrated_database(alembic_config):
    """Run ALL Alembic migrations on a fresh SQLite file before any test runs."""
    url = make_url(settings.database_url)
    assert url.get_backend_name() == "sqlite", f"tests must run on SQLite, not {url.get_backend_name()}"
    db_file = Path(url.database)
    db_file.unlink(missing_ok=True)

    command.upgrade(alembic_config, "head")  # 0001 creates the table, 0002 seeds 6 products
    yield

    engine.dispose()
    db_file.unlink(missing_ok=True)


@pytest.fixture()
def client(alembic_config):
    with TestClient(app) as test_client:
        yield test_client
    # Put the database back to its freshly migrated state, so every test starts the same way.
    engine.dispose()
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")


@pytest.fixture()
def product(client):
    """One extra product saved on top of the seeded data."""
    response = client.post(
        "/api/products",
        json={"name": "Cherry Lip Gloss", "emoji": "🍒", "category": "Beauty", "price": 249, "stock": 80},
    )
    assert response.status_code == 201
    return response.json()
