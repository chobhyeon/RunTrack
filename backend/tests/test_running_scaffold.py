"""Unfinished routes must not look successful or bypass authentication."""
import pytest


ROUTES = [
    ("POST", "/api/running/start"),
    ("POST", "/api/running/session-1/end"),
    ("GET", "/api/running"),
    ("GET", "/api/running/1"),
    ("GET", "/api/running/statistics/summary"),
    ("GET", "/api/running/statistics/weekly"),
    ("GET", "/api/running/statistics/monthly"),
]


@pytest.fixture
def running_client(auth_integration):
    client, _ = auth_integration
    account = {
        "username": "running-scaffold", "email": "runner@example.com",
        "password": "test-only-password",
    }
    assert client.post("/api/users/register", json=account).status_code == 201
    login = client.post("/api/users/login", json=account)
    assert login.status_code == 200
    return client, {"Authorization": "Bearer " + login.json()["access_token"]}


@pytest.mark.parametrize("method,path", ROUTES)
def test_scaffold_requires_auth_and_returns_501(running_client, method, path):
    client, headers = running_client
    unauthorized = client.request(method, path)
    assert unauthorized.status_code == 401
    assert unauthorized.headers["www-authenticate"] == "Bearer"
    response = client.request(method, path, headers=headers)
    assert response.status_code == 501
    assert response.json() == {"detail": "Running feature is not implemented yet"}


@pytest.mark.parametrize("path", [
    "/api/running?skip=-1", "/api/running?limit=0",
    "/api/running?limit=101", "/api/running/0", "/api/running/not-an-id",
])
def test_invalid_parameters_are_rejected(running_client, path):
    client, headers = running_client
    assert client.get(path, headers=headers).status_code == 422
