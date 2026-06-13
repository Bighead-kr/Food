from app.models.schemas import DetectedIngredient, AnalyzeResponse, RecipeRequest, RecipeResponse, IngredientRecord, RecipeRecord


def test_detected_ingredient_requires_name_and_confidence():
    item = DetectedIngredient(name="Apple", confidence=0.91)
    assert item.name == "Apple"
    assert item.confidence == 0.91


def test_analyze_response_holds_ingredient_list():
    response = AnalyzeResponse(ingredients=[DetectedIngredient(name="Apple", confidence=0.91)])
    assert len(response.ingredients) == 1


def test_recipe_request_requires_ingredients_list():
    req = RecipeRequest(ingredients=["Apple", "Tomato"])
    assert req.ingredients == ["Apple", "Tomato"]


def test_recipe_response_has_title_and_content():
    resp = RecipeResponse(title="사과 샐러드", content="재료: 사과\n조리법: 썰어서 담는다")
    assert resp.title == "사과 샐러드"


def test_recipe_request_rejects_empty_list():
    import pytest
    with pytest.raises(Exception):
        RecipeRequest(ingredients=[])
