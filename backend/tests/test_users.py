def test_get_me_success(client, auth_headers):
    resp = client.get("/api/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert data["org_id"] == "test-org-id"


def test_get_me_no_auth(client):
    resp = client.get("/api/me")
    assert resp.status_code == 401


def test_get_me_invalid_token(client):
    resp = client.get("/api/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401
