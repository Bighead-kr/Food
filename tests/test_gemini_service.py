import pytest
from unittest.mock import MagicMock, patch
from app.services.gemini import generate_recipe, parse_recipe_text


def test_parse_recipe_text_extracts_title():
    text = "제목: 사과 샐러드\n재료: 사과\n조리법: 썰어서 담는다"
    title, content = parse_recipe_text(text)
    assert title == "사과 샐러드"
    assert "조리법" in content


def test_parse_recipe_text_fallback_title():
    text = "재료: 사과\n조리법: 썰어서 담는다"
    title, content = parse_recipe_text(text)
    assert title == "AI 추천 레시피"


def test_generate_recipe_calls_gemini_api():
    mock_response = MagicMock()
    mock_response.text = "제목: 사과 구이\n재료: 사과\n조리법: 구워서 먹는다"

    with patch("app.services.gemini.genai") as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        title, content = generate_recipe(["Apple"], api_key="fake-key")

    assert title == "사과 구이"
    assert "조리법" in content


def test_generate_recipe_raises_on_empty_ingredients():
    with pytest.raises(ValueError, match="ingredients must not be empty"):
        generate_recipe([], api_key="fake-key")
