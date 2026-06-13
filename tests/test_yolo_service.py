from unittest.mock import MagicMock
import io
from PIL import Image

from app.services.yolo import run_inference
from app.models.schemas import DetectedIngredient


def _make_image_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_mock_model(class_indices: list, confidences: list, names: dict) -> MagicMock:
    mock_boxes = MagicMock()
    mock_boxes.cls.tolist.return_value = class_indices
    mock_boxes.conf.tolist.return_value = confidences
    mock_result = MagicMock()
    mock_result.boxes = mock_boxes
    mock_result.names = names
    mock_model = MagicMock()
    mock_model.return_value = [mock_result]
    return mock_model


def test_run_inference_returns_detected_ingredients():
    model = _make_mock_model([0], [0.91], {0: "Apple"})
    results = run_inference(model, _make_image_bytes())
    assert len(results) == 1
    assert results[0].name == "Apple"
    assert abs(results[0].confidence - 0.91) < 0.001


def test_run_inference_filters_low_confidence():
    model = _make_mock_model([0], [0.3], {0: "Apple"})
    results = run_inference(model, _make_image_bytes())
    assert results == []


def test_run_inference_deduplicates_same_class():
    model = _make_mock_model([0, 0], [0.85, 0.92], {0: "Apple"})
    results = run_inference(model, _make_image_bytes())
    assert len(results) == 1
    assert abs(results[0].confidence - 0.92) < 0.001


def test_run_inference_returns_empty_on_no_detections():
    model = _make_mock_model([], [], {0: "Apple"})
    results = run_inference(model, _make_image_bytes())
    assert results == []
