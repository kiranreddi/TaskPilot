import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.deps import get_db
from app.main import app
from app.auth import create_access_token
from app import models


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    from app.auth import hash_password

    user = models.User(
        id="test-user-id",
        email="test@example.com",
        name="Test User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.flush()

    org = models.Org(id="test-org-id", name="Test Org", owner_user_id=user.id)
    db_session.add(org)
    db_session.flush()

    membership = models.Membership(user_id=user.id, org_id=org.id, role="OWNER")
    db_session.add(membership)
    db_session.commit()

    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"user_id": test_user.id, "org_id": "test-org-id", "role": "OWNER"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def member_user(db_session):
    from app.auth import hash_password

    user = models.User(
        id="member-user-id",
        email="member@example.com",
        name="Member User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.flush()

    membership = models.Membership(user_id=user.id, org_id="test-org-id", role="MEMBER")
    db_session.add(membership)
    db_session.commit()
    return user


@pytest.fixture
def member_headers(test_user, member_user):
    token = create_access_token({"user_id": member_user.id, "org_id": "test-org-id", "role": "MEMBER"})
    return {"Authorization": f"Bearer {token}"}
