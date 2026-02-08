def test_signup_success(client):
    resp = client.post("/api/auth/signup", json={
        "email": "new@example.com",
        "password": "secret123",
        "name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_signup_duplicate_email(client):
    client.post("/api/auth/signup", json={
        "email": "dup@example.com",
        "password": "secret123",
        "name": "First",
    })
    resp = client.post("/api/auth/signup", json={
        "email": "dup@example.com",
        "password": "secret123",
        "name": "Second",
    })
    assert resp.status_code == 409


def test_signup_missing_fields(client):
    resp = client.post("/api/auth/signup", json={"email": "a@b.com"})
    assert resp.status_code == 422


def test_login_success(client):
    client.post("/api/auth/signup", json={
        "email": "login@example.com",
        "password": "secret123",
        "name": "Login User",
    })
    resp = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/api/auth/signup", json={
        "email": "wrong@example.com",
        "password": "secret123",
        "name": "User",
    })
    resp = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post("/api/auth/login", json={
        "email": "nobody@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 401
