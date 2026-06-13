from unittest.mock import MagicMock
from app.services.supabase_client import save_ingredients, save_recipe, get_ingredients, get_recipes
from app.models.schemas import DetectedIngredient


def _make_client() -> MagicMock:
    client = MagicMock()
    table_mock = MagicMock()
    client.table.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.select.return_value = table_mock
    table_mock.order.return_value = table_mock
    table_mock.limit.return_value = table_mock
    table_mock.execute.return_value = MagicMock(data=[])
    return client


def test_save_ingredients_calls_insert():
    client = _make_client()
    ingredients = [DetectedIngredient(name="Apple", confidence=0.91)]
    save_ingredients(client, ingredients)
    client.table.assert_called_with("ingredients")
    client.table().insert.assert_called_once()
    inserted = client.table().insert.call_args[0][0]
    assert inserted[0]["name"] == "Apple"
    assert inserted[0]["confidence"] == 0.91


def test_save_recipe_calls_insert():
    client = _make_client()
    save_recipe(client, ["Apple"], "사과 샐러드", "재료: 사과\n조리법: 썰기")
    client.table.assert_called_with("recipes")
    client.table().insert.assert_called_once()
    inserted = client.table().insert.call_args[0][0]
    assert inserted["title"] == "사과 샐러드"
    assert inserted["ingredients"] == ["Apple"]


def test_get_ingredients_returns_list():
    client = _make_client()
    client.table().execute.return_value = MagicMock(data=[
        {"id": "abc", "name": "Apple", "confidence": 0.91, "detected_at": "2026-06-13T00:00:00"}
    ])
    results = get_ingredients(client)
    assert len(results) == 1
    assert results[0]["name"] == "Apple"


def test_get_recipes_returns_list():
    client = _make_client()
    client.table().execute.return_value = MagicMock(data=[
        {"id": "xyz", "ingredients": ["Apple"], "title": "사과 샐러드", "content": "...", "created_at": "2026-06-13T00:00:00"}
    ])
    results = get_recipes(client)
    assert len(results) == 1
    assert results[0]["title"] == "사과 샐러드"
