"""Verify new Backend 2 routes, validation and provider boundaries."""
import pytest

from app.api.routes.recommendations import get_recommendation_service
from app.api.routes.weather import get_weather_service
from app.main import app


RECOMMENDATION = {
    "weight_kg": 65, "height_cm": 175, "foot_size": "270mm",
    "foot_width": "regular", "arch_type": "normal",
    "running_style": "cushioning", "budget_won": 150000,
}
NEW_ROUTES = [
    ("PUT", "/api/running/1", {"notes": "easy run"}),
    ("DELETE", "/api/running/1", None),
    ("GET", "/api/weather/advice?latitude=37.5&longitude=127", None),
    ("GET", "/api/weather/history?latitude=37.5&longitude=127", None),
    ("POST", "/api/recommendations/shoes", RECOMMENDATION),
]


@pytest.fixture
def client_with_token(auth_integration):
    client, _ = auth_integration
    account = {"username": "backend2", "email": "backend2@example.com", "password": "test-only-password"}
    assert client.post("/api/users/register", json=account).status_code == 201
    login = client.post("/api/users/login", json=account)
    assert login.status_code == 200
    return client, {"Authorization": "Bearer " + login.json()["access_token"]}


@pytest.mark.parametrize("method,path,payload", NEW_ROUTES)
def test_authentication_and_explicit_unimplemented_response(client_with_token, method, path, payload):
    client, headers = client_with_token
    assert client.request(method, path, json=payload).status_code == 401
    response = client.request(method, path, json=payload, headers=headers)
    assert response.status_code == 501
    assert "not implemented" in response.json()["detail"]


@pytest.mark.parametrize("method,path,payload", [
    ("PUT", "/api/running/1", {"user_id": 2}),
    ("PUT", "/api/running/1", {"shoe_id": 0}),
    ("DELETE", "/api/running/0", None),
    ("GET", "/api/weather/advice?latitude=91&longitude=0", None),
    ("GET", "/api/weather/advice?latitude=0&longitude=-181", None),
    ("GET", "/api/weather/advice", None),
    ("GET", "/api/weather/history?latitude=0&longitude=0&days=0", None),
    ("GET", "/api/weather/history?latitude=0&longitude=0&days=31", None),
    ("POST", "/api/recommendations/shoes", {}),
    ("POST", "/api/recommendations/shoes", {**RECOMMENDATION, "weight_kg": -1}),
    ("POST", "/api/recommendations/shoes", {**RECOMMENDATION, "foot_size": "  "}),
    ("POST", "/api/recommendations/shoes", {**RECOMMENDATION, "user_id": 2}),
])
def test_invalid_requests(client_with_token, method, path, payload):
    client, headers = client_with_token
    assert client.request(method, path, json=payload, headers=headers).status_code == 422


def test_provider_injection_and_request_forwarding(client_with_token):
    client, headers = client_with_token
    received = {}

    class WeatherStub:
        async def advice(self, latitude, longitude):
            received["location"] = (latitude, longitude)
            return {
                "latitude": latitude, "longitude": longitude,
                "temperature_c": 20, "perceived_temperature_c": 19,
                "humidity_percent": 50, "wind_speed_kmh": 5,
                "condition": "test fixture", "tips": [],
            }

    class RecommendationStub:
        async def get_shoe_recommendations(self, **values):
            received["profile"] = values
            return {"recommendations": [{"brand": "Test", "model": "Fixture", "reason": "test only"}]}

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_weather_service] = lambda: WeatherStub()
    app.dependency_overrides[get_recommendation_service] = lambda: RecommendationStub()
    try:
        weather = client.get("/api/weather/advice?latitude=37.5&longitude=127", headers=headers)
        assert weather.status_code == 200
        assert received["location"] == (37.5, 127.0)
        assert weather.json()["running_score"] is None
        result = client.post("/api/recommendations/shoes", json=RECOMMENDATION, headers=headers)
        assert result.status_code == 200
        assert received["profile"] == {**RECOMMENDATION, "preferred_brands": None}
        assert result.json()["recommendations"][0]["brand"] == "Test"
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def test_openapi_exposes_all_backend2_routes_with_security():
    paths = app.openapi()["paths"]
    operations = [
        ("post", "/api/running/start"), ("post", "/api/running/{session_id}/end"),
        ("get", "/api/running"), ("get", "/api/running/{record_id}"),
        ("put", "/api/running/{record_id}"), ("delete", "/api/running/{record_id}"),
        ("get", "/api/running/statistics/summary"),
        ("get", "/api/running/statistics/weekly"), ("get", "/api/running/statistics/monthly"),
        ("get", "/api/weather/advice"), ("get", "/api/weather/history"),
        ("post", "/api/recommendations/shoes"),
    ]
    for method, path in operations:
        operation = paths[path][method]
        assert operation["security"] == [{"HTTPBearer": []}]
        assert "501" in operation["responses"]
