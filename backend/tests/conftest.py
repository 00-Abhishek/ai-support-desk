import os
import tempfile

# The application engine is created at import time, so point it at a shared
# temporary SQLite file before importing the app. Tests override the request
# session with their own in-memory database.
_tmp_db = os.path.join(tempfile.mkdtemp(), "app_test.db")
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{_tmp_db}"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSession()
    db.add_all([
        User(email="admin@example.com", full_name="Ada Admin", role="admin", hashed_password=hash_password("admin123")),
        User(email="agent@example.com", full_name="Grace Agent", role="agent", hashed_password=hash_password("agent123")),
        User(email="requester@example.com", full_name="Ravi Requester", role="requester", hashed_password=hash_password("request123")),
    ])
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def auth_headers(client, email, password):
    resp = client.post("/api/auth/token", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
