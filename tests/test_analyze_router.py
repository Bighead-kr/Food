import io
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from PIL import Image

from app.routers.analyze import router
from app.models.schemas import DetectedIngredient


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.state.model = MagicMock()
    return app


def _make_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_analyze_returns_ingredients():
    app = _make_app()
    client = TestClient(app)

    with patch("app.routers.analyze.run_inference") as mock_infer, \
         patch("app.routers.analyze.save_ingredients") as mock_save, \
         patch("app.routers.analyze.get_client") as mock_db:

        mock_infer.return_value = [DetectedIngredient(name="Apple", confidence=0.91)]
        mock_db.return_value = MagicMock()

        response = client.post(
            "/analyze",
            files={"file": ("apple.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["ingredients"][0]["name"] == "Apple"
    assert mock_save.called


def test_analyze_returns_empty_on_no_detections():
    app = _make_app()
    client = TestClient(app)

    with patch("app.routers.analyze.run_inference") as mock_infer, \
         patch("app.routers.analyze.save_ingredients"), \
         patch("app.routers.analyze.get_client"):

        mock_infer.return_value = []

        response = client.post(
            "/analyze",
            files={"file": ("empty.jpg", _make_jpeg_bytes(), "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["ingredients"] == []
