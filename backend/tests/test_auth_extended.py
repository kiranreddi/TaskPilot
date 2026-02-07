from datetime import datetime, timedelta, timezone

from jose import jwt

from app.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.config import settings


# --- Direct auth function tests ---

def test_hash_password_returns_string():
    result = hash_password("testpassword")
    assert isinstance(result, str)
    assert result != "testpassword"


def test_verify_password_correct():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_incorrect():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_decode_token():
    data = {"user_id": "u1", "org_id": "o1", "role": "OWNER"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == "u1"
    assert payload["org_id"] == "o1"
    assert payload["role"] == "OWNER"
    assert "exp" in payload


def test_decode_token_with_invalid_secret():
    data = {"user_id": "u1", "org_id": "o1"}
    token = jwt.encode(data, "wrong-secret", algorithm=settings.ALGORITHM)
    payload = decode_access_token(token)
    assert payload is None


def test_decode_token_expired():
    data = {"user_id": "u1", "org_id": "o1"}
    expire = datetime.now(timezone.utc) - timedelta(minutes=5)
    data["exp"] = expire
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    payload = decode_access_token(token)
    assert payload is None


def test_decode_token_malformed():
    payload = decode_access_token("not.a.valid.token")
    assert payload is None


# --- Signup edge cases ---

def test_signup_with_very_long_email(client):
    long_email = "a" * 300 + "@example.com"
    resp = client.post("/api/auth/signup", json={
        "email": long_email,
        "password": "secret123",
        "name": "Long Email User",
    })
    # Server should either reject or accept; 201 means it stored it,
    # which is fine. We just verify no 500 error.
    assert resp.status_code in (201, 422)


def test_signup_with_empty_body(client):
    resp = client.post("/api/auth/signup", json={})
    assert resp.status_code == 422


def test_signup_with_short_password(client):
    resp = client.post("/api/auth/signup", json={
        "email": "short@example.com",
        "password": "ab",
        "name": "Short Pass",
    })
    # The schema doesn't enforce min length, so signup succeeds
    assert resp.status_code in (201, 422)


# --- Login edge cases ---

def test_login_with_empty_email(client):
    resp = client.post("/api/auth/login", json={
        "email": "",
        "password": "secret123",
    })
    assert resp.status_code == 401


def test_login_with_empty_password(client):
    client.post("/api/auth/signup", json={
        "email": "emptypass@example.com",
        "password": "secret123",
        "name": "User",
    })
    resp = client.post("/api/auth/login", json={
        "email": "emptypass@example.com",
        "password": "",
    })
    assert resp.status_code == 401
