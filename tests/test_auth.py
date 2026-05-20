def test_register(client):
    r = client.post("/auth/register", json={"email": "user@example.com", "password": "secret"})
    assert r.status_code == 201


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "user@example.com", "password": "secret"})
    r = client.post("/auth/register", json={"email": "user@example.com", "password": "other"})
    assert r.status_code == 400


def test_login(client):
    client.post("/auth/register", json={"email": "user@example.com", "password": "secret"})
    r = client.post("/auth/login", json={"email": "user@example.com", "password": "secret"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "user@example.com", "password": "secret"})
    r = client.post("/auth/login", json={"email": "user@example.com", "password": "wrong"})
    assert r.status_code == 401


def test_forgot_password_always_200(client):
    r = client.post("/auth/forgot-password", json={"email": "nobody@example.com"})
    assert r.status_code == 200


def test_reset_password(client):
    from datetime import datetime, timedelta, timezone

    from app.models.user import PasswordResetToken, User
    from app.services.auth import hash_password
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    user = User(email="user@example.com", hashed_password=hash_password("old"))
    db.add(user)
    db.flush()
    token = PasswordResetToken(
        user_id=user.id,
        token="valid-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(token)
    db.commit()
    db.close()

    r = client.post("/auth/reset-password", json={"token": "valid-token", "new_password": "new"})
    assert r.status_code == 200


def test_reset_password_invalid_token(client):
    r = client.post("/auth/reset-password", json={"token": "bad-token", "new_password": "new"})
    assert r.status_code == 400
