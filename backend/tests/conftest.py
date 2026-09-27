import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.config import settings
from app.database import engine as configured_engine


@pytest.fixture(autouse=True)
def isolate_auth_settings_and_configured_database(monkeypatch):
    """Never sign test tokens with a local secret or connect to the configured DB."""
    monkeypatch.setattr(settings, "SECRET_KEY", "isolated-test-only-signing-key")
    monkeypatch.setattr(settings, "ALGORITHM", "HS256")
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30)

    def disallow_connection(*args, **kwargs):
        raise AssertionError("Tests must not connect to the configured database")

    monkeypatch.setattr(configured_engine, "connect", disallow_connection)


@pytest.fixture
def auth_integration(tmp_path):
    """Temporary SQLite DB, with a fresh session for each HTTP request."""
    engine = create_engine(
        "sqlite:///" + (tmp_path / "auth-test.sqlite3").as_posix(),
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    def override_get_db():
        with factory() as session:
            yield session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()

