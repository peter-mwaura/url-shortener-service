import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app

# --------------------------
# Setup test database (Postgres)
# --------------------------
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "url_shortener")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables before tests
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


# Dependency override for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# --------------------------
# Test cases
# --------------------------
def test_create_short_url_random():
    response = client.post("/shorten", json={"original_url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert data["short_url"].startswith(
        os.getenv("SHORT_URL_DOMAIN", "http://localhost:8000/")
    )


def test_create_short_url_custom_alias():
    response = client.post(
        "/shorten",
        json={"original_url": "https://example.com", "custom_alias": "myalias"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["short_url"].endswith("/myalias")


def test_create_short_url_duplicate_custom_alias():
    # First creation
    client.post(
        "/shorten",
        json={"original_url": "https://example.com", "custom_alias": "duplicate"},
    )

    # Attempt duplicate
    response = client.post(
        "/shorten",
        json={"original_url": "https://another.com", "custom_alias": "duplicate"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Custom alias already in use"


def test_generate_unique_short_code(monkeypatch):
    import random

    from app.api import shorten

    # Patch random.choices to always return the same code
    def fake_choices(*args, **kwargs):
        return list("abcdef")

    monkeypatch.setattr(random, "choices", fake_choices)

    # Patch rate limiter to bypass it
    monkeypatch.setattr(shorten, "check_rate_limit", lambda client_ip: None)

    # First call works
    response = client.post("/shorten", json={"original_url": "https://example1.com"})
    assert response.status_code == 200

    # Next 5 attempts should fail due to collision
    for i in range(5):
        response = client.post(
            "/shorten", json={"original_url": f"https://example{i+2}.com"}
        )
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to generate unique short code"


def test_rate_limiting(monkeypatch):
    from app.api import shorten

    # Patch short code generator to return unique codes to avoid collisions
    codes = [f"code{i}" for i in range(100)]
    iter_codes = iter(codes)
    monkeypatch.setattr(
        shorten, "generate_short_code", lambda length=6: next(iter_codes)
    )

    # Reset Redis for test
    import redis

    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True,
    )
    r.flushdb()

    # Exceed the rate limit
    limit = int(os.getenv("RATE_LIMIT", 5))

    for i in range(limit):
        response = client.post("/shorten", json={"original_url": f"https://ex{i}.com"})
        assert response.status_code == 200

    # Next request should be blocked
    response = client.post("/shorten", json={"original_url": "https://blocked.com"})
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
