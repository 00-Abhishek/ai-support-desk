from tests.conftest import auth_headers


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_login_and_me(client):
    headers = auth_headers(client, "agent@example.com", "agent123")
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "agent@example.com"


def test_login_wrong_password(client):
    resp = client.post("/api/auth/token", data={"username": "agent@example.com", "password": "nope"})
    assert resp.status_code == 401


def test_unauthenticated_is_401(client):
    resp = client.get("/api/tickets")
    assert resp.status_code == 401
