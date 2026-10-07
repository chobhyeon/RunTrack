"""Integration-style API tests for authenticated shoe management."""


def register_and_login(client, username, email):
    account = {
        "username": username,
        "email": email,
        "password": "test-only-password",
    }
    registered = client.post("/api/users/register", json=account)
    assert registered.status_code == 201
    login = client.post("/api/users/login", json=account)
    assert login.status_code == 200
    return {"Authorization": "Bearer " + login.json()["access_token"]}


def test_shoe_crud_and_partial_update_preserves_other_fields(auth_integration):
    client, _ = auth_integration
    headers = register_and_login(
        client, "shoe-owner", "shoe-owner@example.com",
    )
    payload = {
        "brand": "Nike",
        "model": "Pegasus",
        "size": "270",
        "color": "Black",
        "purchase_price_won": 159000,
        "notes": "test shoe",
    }

    created = client.post("/api/shoes", headers=headers, json=payload)

    assert created.status_code == 201
    shoe = created.json()
    shoe_id = shoe["id"]
    assert shoe["user_id"] > 0
    assert shoe["brand"] == payload["brand"]
    assert shoe["model"] == payload["model"]
    assert shoe["cumulative_km"] == 0
    assert shoe["run_count"] == 0
    assert shoe["condition"] == "good"

    listed = client.get("/api/shoes", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [shoe_id]

    detail = client.get(f"/api/shoes/{shoe_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json() == shoe

    updated = client.put(
        f"/api/shoes/{shoe_id}",
        headers=headers,
        json={"color": "White", "brand": None},
    )
    assert updated.status_code == 200
    assert updated.json()["color"] == "White"
    assert updated.json()["brand"] == "Nike"
    assert updated.json()["model"] == "Pegasus"
    assert updated.json()["size"] == "270"
    assert updated.json()["purchase_price_won"] == 159000
    assert updated.json()["notes"] == "test shoe"

    stats = client.get(f"/api/shoes/{shoe_id}/stats", headers=headers)
    assert stats.status_code == 200
    assert stats.json() == {
        "cumulative_km": 0.0,
        "run_count": 0,
        "condition": "good",
    }

    deleted = client.delete(f"/api/shoes/{shoe_id}", headers=headers)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/api/shoes/{shoe_id}", headers=headers).status_code == 404


def test_shoe_routes_require_authentication(auth_integration):
    client, _ = auth_integration

    responses = [
        client.post("/api/shoes", json={"brand": "Nike", "model": "Pegasus"}),
        client.get("/api/shoes"),
        client.get("/api/shoes/1"),
        client.put("/api/shoes/1", json={"color": "White"}),
        client.delete("/api/shoes/1"),
        client.get("/api/shoes/1/stats"),
    ]

    for response in responses:
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


def test_users_cannot_read_or_change_another_users_shoe(auth_integration):
    client, _ = auth_integration
    owner_headers = register_and_login(
        client, "shoe-owner-two", "shoe-owner-two@example.com",
    )
    other_headers = register_and_login(
        client, "shoe-other", "shoe-other@example.com",
    )
    created = client.post(
        "/api/shoes",
        headers=owner_headers,
        json={"brand": "Asics", "model": "Novablast", "size": "270"},
    )
    assert created.status_code == 201
    shoe_id = created.json()["id"]

    assert client.get("/api/shoes", headers=other_headers).json() == []
    assert client.get(f"/api/shoes/{shoe_id}", headers=other_headers).status_code == 404
    assert client.get(f"/api/shoes/{shoe_id}/stats", headers=other_headers).status_code == 404
    assert client.put(
        f"/api/shoes/{shoe_id}", headers=other_headers, json={"color": "Red"},
    ).status_code == 404
    assert client.delete(
        f"/api/shoes/{shoe_id}", headers=other_headers,
    ).status_code == 404

    owner_view = client.get(f"/api/shoes/{shoe_id}", headers=owner_headers)
    assert owner_view.status_code == 200
    assert owner_view.json()["color"] is None


def test_shoe_ids_must_be_positive_integers(auth_integration):
    client, _ = auth_integration
    headers = register_and_login(
        client, "shoe-validator", "shoe-validator@example.com",
    )

    assert client.get("/api/shoes/0", headers=headers).status_code == 422
    assert client.get("/api/shoes/not-an-id", headers=headers).status_code == 422
