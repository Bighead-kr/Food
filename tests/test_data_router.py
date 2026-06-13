from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routers.data import router


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def test_get_ingredients_returns_list():
    app = _make_app()
    client = TestClient(app)

    with patch("app.routers.data.get_client") as mock_db, \
         patch("app.routers.data.get_ingredients") as mock_get:

        mock_get.return_value = [
            {"id": "abc", "name": "Apple", "confidence": 0.91, "detected_at": "2026-06-13T00:00:00"}
        ]

        response = client.get("/ingredients")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Apple"


def test_get_recipes_returns_list():
    app = _make_app()
    client = TestClient(app)

    with patch("app.routers.data.get_client") as mock_db, \
         patch("app.routers.data.get_recipes") as mock_get:

        mock_get.return_value = [
            {"id": "xyz", "ingredients": ["Apple"], "title": "사과 샐러드", "content": "...", "created_at": "2026-06-13T00:00:00"}
        ]

        response = client.get("/recipes")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["title"] == "사과 샐러드"
