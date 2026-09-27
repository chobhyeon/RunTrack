"""Verify the complete auth contract across independent HTTP request sessions."""
import json
from datetime import datetime, timezone

import pytest
from jose import jwt
from sqlalchemy import func, select

from app.config import settings
from app.core.security import verify_password
from app.models import User


ACCOUNT = {
    "username": "integration-runner",
    "email": "integration@example.com",
    "password": "  integration-password\t ",
    "weight_kg": 65.0,
    "preferred_brands": ["Nike"],
}


def assert_no_password(response, hashed_password=None):
    def check(value):
        if isinstance(value, dict):
            assert not {"password", "hashed_password"} & value.keys()
            for child in value.values():
                check(child)
        elif isinstance(value, list):
            for child in value:
                check(child)
    check(response.json())
    assert ACCOUNT["password"] not in response.text
    assert ACCOUNT["password"].strip() not in response.text
    if hashed_password:
        assert hashed_password not in response.text


def register_and_login(client):
    registered = client.post("/api/users/register", json=ACCOUNT)
    assert registered.status_code == 201
    assert_no_password(registered)
    login = client.post("/api/users/login", json={
        "username": ACCOUNT["username"], "password": ACCOUNT["password"],
    })
    assert login.status_code == 200
    assert_no_password(login)
    return registered.json(), login.json()["access_token"]


def test_complete_auth_flow_and_persisted_profile(auth_integration):
    client, factory = auth_integration
    registered, token = register_and_login(client)
    headers = {"Authorization": "Bearer " + token}
    with factory() as session:
        stored = session.get(User, registered["id"])
        password_hash = stored.hashed_password
        assert password_hash != ACCOUNT["password"]
        assert verify_password(ACCOUNT["password"], password_hash)

    profile = client.get("/api/users/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json() == registered
    assert_no_password(profile, password_hash)
    updated = client.put("/api/users/me", headers=headers, json={
        "weight_kg": 66.5, "height_cm": 175, "preferred_brands": ["아디다스"],
    })
    assert updated.status_code == 200
    assert updated.json()["id"] == registered["id"]
    assert updated.json()["username"] == ACCOUNT["username"]
    assert updated.json()["weight_kg"] == 66.5
    assert updated.json()["height_cm"] == 175
    assert updated.json()["preferred_brands"] == ["아디다스"]
    assert_no_password(updated, password_hash)
    reread = client.get("/api/users/me", headers=headers)
    assert reread.status_code == 200 and reread.json() == updated.json()
    assert_no_password(reread, password_hash)
    with factory() as session:
        stored = session.get(User, registered["id"])
        assert stored.weight_kg == 66.5
        assert json.loads(stored.preferred_brands) == ["아디다스"]
        assert stored.hashed_password == password_hash


@pytest.mark.parametrize("changes", [{"email": "different@example.com"}, {"username": "different"}])
def test_duplicate_registration_is_rejected(auth_integration, changes):
    client, factory = auth_integration
    register_and_login(client)
    response = client.post("/api/users/register", json={**ACCOUNT, **changes})
    assert response.status_code == 409
    assert response.json() == {"detail": "Username or email already exists"}
    assert_no_password(response)
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 1


def test_wrong_credentials_return_identical_errors(auth_integration):
    client, _ = auth_integration
    register_and_login(client)
    responses = [client.post("/api/users/login", json=payload) for payload in (
        {"username": ACCOUNT["username"], "password": "wrong"},
        {"username": "nonexistent", "password": ACCOUNT["password"]},
    )]
    for response in responses:
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid username or password"}
        assert_no_password(response)


@pytest.mark.parametrize("kind", ["missing", "expired", "tampered", "deleted-user"])
def test_rejected_tokens_cannot_read_or_modify(auth_integration, kind):
    client, factory = auth_integration
    registered, token = register_and_login(client)
    if kind == "expired":
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        payload["exp"] = int(datetime.now(timezone.utc).timestamp()) - 1
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    elif kind == "tampered":
        parts = token.split(".")
        parts[2] = ("A" if parts[2][0] != "A" else "B") + parts[2][1:]
        token = ".".join(parts)
    elif kind == "deleted-user":
        with factory() as session:
            session.delete(session.get(User, registered["id"]))
            session.commit()
    headers = {} if kind == "missing" else {"Authorization": "Bearer " + token}
    for response in (
        client.get("/api/users/me", headers=headers),
        client.put("/api/users/me", headers=headers, json={"weight_kg": 99}),
    ):
        assert response.status_code == 401
        assert response.json() == {"detail": "Could not validate credentials"}
        assert response.headers["www-authenticate"] == "Bearer"
        assert_no_password(response)
    with factory() as session:
        stored = session.get(User, registered["id"])
        if kind == "deleted-user":
            assert stored is None
        else:
            assert stored.weight_kg == ACCOUNT["weight_kg"]
