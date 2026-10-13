from tests.conftest import auth_headers


def make_ticket(client, headers, **overrides):
    payload = {"title": "Cannot reset password", "description": "Reset link expired", "priority": "High", "category": "account"}
    payload.update(overrides)
    return client.post("/api/tickets", json=payload, headers=headers)


def test_create_and_list_ticket(client):
    headers = auth_headers(client, "requester@example.com", "request123")
    resp = make_ticket(client, headers)
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "Open"

    listing = client.get("/api/tickets", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1


def test_invalid_priority_rejected(client):
    headers = auth_headers(client, "requester@example.com", "request123")
    resp = make_ticket(client, headers, priority="Whenever")
    assert resp.status_code == 422


def test_status_transition_enforced(client):
    requester = auth_headers(client, "requester@example.com", "request123")
    agent = auth_headers(client, "agent@example.com", "agent123")
    ticket_id = make_ticket(client, requester).json()["id"]

    # Open -> In Progress is allowed
    ok = client.patch(f"/api/tickets/{ticket_id}", json={"status": "In Progress"}, headers=agent)
    assert ok.status_code == 200

    # In Progress -> Closed is NOT allowed (must go via Resolved)
    bad = client.patch(f"/api/tickets/{ticket_id}", json={"status": "Closed"}, headers=agent)
    assert bad.status_code == 422


def test_requester_cannot_update(client):
    requester = auth_headers(client, "requester@example.com", "request123")
    ticket_id = make_ticket(client, requester).json()["id"]
    resp = client.patch(f"/api/tickets/{ticket_id}", json={"priority": "Urgent"}, headers=requester)
    assert resp.status_code == 403


def test_comment_and_ai_suggest(client):
    requester = auth_headers(client, "requester@example.com", "request123")
    agent = auth_headers(client, "agent@example.com", "agent123")
    ticket_id = make_ticket(client, requester).json()["id"]

    c = client.post(f"/api/tickets/{ticket_id}/comments", json={"body": "Looking into it"}, headers=agent)
    assert c.status_code == 201

    ai = client.post(f"/api/tickets/{ticket_id}/ai-suggest", headers=agent)
    assert ai.status_code == 200
    body = ai.json()
    assert body["category"] == "account"
    assert body["priority"] in ("Low", "Medium", "High", "Urgent")


def test_dashboard_counts(client):
    headers = auth_headers(client, "agent@example.com", "agent123")
    resp = client.get("/api/dashboard/summary", headers=headers)
    assert resp.status_code == 200
    assert "open" in resp.json()
