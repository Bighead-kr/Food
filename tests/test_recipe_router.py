import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routers.recipe import router


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def test_recipe_returns_title_and_content():
    app = _make_app()
    client = TestClient(app)

    with patch("app.routers.recipe.generate_recipe") as mock_gen, \
         patch("app.routers.recipe.save_recipe") as mock_save, \
         patch("app.routers.recipe.get_client"), \
         patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):

        mock_gen.return_value = ("사과 구이", "재료: 사과\n조리법: 구워서 먹는다")

        response = client.post("/recipe", json={"ingredients": ["Apple"]})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "사과 구이"
    assert "조리법" in data["content"]
    assert mock_save.called


def test_recipe_rejects_empty_ingredients():
    app = _make_app()
    client = TestClient(app)
    response = client.post("/recipe", json={"ingredients": []})
    assert response.status_code == 422
