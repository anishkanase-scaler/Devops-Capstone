from alembic import command
from sqlalchemy import create_engine, inspect, text

from app.config import settings


def test_seeded_database_is_at_latest_migration(client):
    # The session fixture already ran `alembic upgrade head` on the test database.
    with create_engine(settings.database_url).connect() as conn:
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0002_seed_products"
        assert conn.execute(text("SELECT COUNT(*) FROM products")).scalar() == 6


def test_migrations_roll_back_cleanly(alembic_config, tmp_path, monkeypatch):
    # Upgrade and downgrade the real migrations on a separate, temporary SQLite file.
    url = f"sqlite:///{tmp_path / 'migrations.db'}"
    monkeypatch.setattr(settings, "database_url", url)  # alembic/env.py reads the URL from settings
    engine = create_engine(url)

    command.upgrade(alembic_config, "head")
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM products")).scalar() == 6

    command.downgrade(alembic_config, "0001_create_products")  # removes only the seed data
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM products")).scalar() == 0

    command.downgrade(alembic_config, "base")  # drops the table
    assert "products" not in inspect(engine).get_table_names()
    engine.dispose()
