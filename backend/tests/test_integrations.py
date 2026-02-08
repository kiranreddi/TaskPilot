def test_list_integrations(client):
    resp = client.get("/api/integrations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5
    providers = [i["provider"] for i in data]
    assert "google" in providers
    assert "slack" in providers


def test_list_connections_empty(client, auth_headers):
    resp = client.get("/api/connections", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_connections_no_auth(client):
    resp = client.get("/api/connections")
    assert resp.status_code == 401


def test_start_oauth(client, auth_headers):
    resp = client.post("/api/connections/google/start", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "authorize_url" in data
    assert "connection_id" in data


def test_start_oauth_unknown_provider(client, auth_headers):
    resp = client.post("/api/connections/unknown/start", headers=auth_headers)
    assert resp.status_code == 404


def test_start_oauth_no_auth(client):
    resp = client.post("/api/connections/google/start")
    assert resp.status_code == 401


def test_list_connections_after_oauth(client, auth_headers):
    client.post("/api/connections/google/start", headers=auth_headers)
    resp = client.get("/api/connections", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["provider"] == "google"
    assert data[0]["status"] == "CONNECTED"


def test_connect_multiple_providers(client, auth_headers):
    client.post("/api/connections/google/start", headers=auth_headers)
    client.post("/api/connections/slack/start", headers=auth_headers)
    resp = client.get("/api/connections", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    providers = {c["provider"] for c in data}
    assert providers == {"google", "slack"}


def test_list_connections_returns_correct_structure(client, auth_headers):
    client.post("/api/connections/google/start", headers=auth_headers)
    resp = client.get("/api/connections", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    item = data[0]
    assert "id" in item
    assert "org_id" in item
    assert "provider" in item
    assert "status" in item
    assert "scopes" in item
