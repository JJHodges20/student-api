"""
Shared pytest fixtures for the Student API test suite.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# ============================================================
# TEST DATABASE
# ============================================================

TEST_DATABASE_URL = "sqlite://"


test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    """
    Replace the development database dependency
    with the test database.
    """

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ============================================================
# DATABASE RESET
# ============================================================

@pytest.fixture(autouse=True)
def reset_database():
    """
    Give every test a fresh database.
    """

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


# ============================================================
# TEST CLIENT
# ============================================================

@pytest.fixture
def client():
    """Return a FastAPI test client."""

    with TestClient(app) as test_client:
        yield test_client


# ============================================================
# AUTHENTICATION
# ============================================================

@pytest.fixture
def auth_headers():
    """
    Create a test user directly in the test database
    and return a valid JWT Authorization header.

    This avoids consuming the /auth/login rate limit
    during every authenticated CRUD test.
    """

    from app.models.user import User
    from app.utils.security import (
        create_access_token,
        hash_password,
    )

    db = TestingSessionLocal()

    try:
        user = User(
            username="testuser",
            hashed_password=hash_password(
                "testpassword123"
            ),
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token(
            user.id
        )

        return {
            "Authorization": f"Bearer {token}"
        }

    finally:
        db.close()


# ============================================================
# SAMPLE STUDENT
# ============================================================

@pytest.fixture
def sample_student(
    client,
    auth_headers,
):
    """
    Create a student that can be reused
    by other tests.
    """

    response = client.post(
        "/students/",
        headers=auth_headers,
        json={
            "name": "Test Student",
            "email": "student@example.com",
            "grade_level": 10,
            "gpa": 3.5,
            "is_enrolled": False,
        },
    )

    assert response.status_code == 201

    return response.json()