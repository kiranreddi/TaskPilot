def test_list_members(client, auth_headers):
    resp = client.get("/api/admin/members", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["role"] == "OWNER"


def test_list_members_no_auth(client):
    resp = client.get("/api/admin/members")
    assert resp.status_code == 401


def test_list_members_non_admin(client, member_headers):
    resp = client.get("/api/admin/members", headers=member_headers)
    assert resp.status_code == 403


def test_invite_member(client, auth_headers):
    resp = client.post("/api/admin/members/invite", headers=auth_headers, json={
        "email": "invited@example.com",
        "role": "MEMBER",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "invited@example.com"
    assert data["role"] == "MEMBER"


def test_invite_member_duplicate(client, auth_headers):
    client.post("/api/admin/members/invite", headers=auth_headers, json={
        "email": "dup@example.com",
        "role": "MEMBER",
    })
    resp = client.post("/api/admin/members/invite", headers=auth_headers, json={
        "email": "dup@example.com",
        "role": "MEMBER",
    })
    assert resp.status_code == 409


def test_invite_member_no_auth(client):
    resp = client.post("/api/admin/members/invite", json={
        "email": "x@example.com",
        "role": "MEMBER",
    })
    assert resp.status_code == 401


def test_invite_member_non_admin(client, member_headers):
    resp = client.post("/api/admin/members/invite", headers=member_headers, json={
        "email": "x@example.com",
        "role": "MEMBER",
    })
    assert resp.status_code == 403


def test_get_policies(client, auth_headers):
    resp = client.get("/api/admin/policies", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "require_approval_for_write" in data


def test_get_policies_no_auth(client):
    resp = client.get("/api/admin/policies")
    assert resp.status_code == 401


def test_update_policies(client, auth_headers):
    resp = client.put("/api/admin/policies", headers=auth_headers, json={
        "require_approval_for_write": False,
    })
    assert resp.status_code == 200
    assert resp.json()["require_approval_for_write"] is False

    # Verify it persisted
    resp = client.get("/api/admin/policies", headers=auth_headers)
    assert resp.json()["require_approval_for_write"] is False


def test_update_policies_no_auth(client):
    resp = client.put("/api/admin/policies", json={"require_approval_for_write": False})
    assert resp.status_code == 401


def test_update_policies_non_admin(client, member_headers):
    resp = client.put("/api/admin/policies", headers=member_headers, json={
        "require_approval_for_write": False,
    })
    assert resp.status_code == 403
