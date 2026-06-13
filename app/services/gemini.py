import google.generativeai as genai


_PROMPT_TEMPLATE = """다음 재료를 사용한 간단한 레시피를 한국어로 추천해줘.
재료: {ingredients}

형식:
제목: [레시피 이름]
재료: [목록]
조리법: [단계별 설명]
주의: 주어진 재료만 사용하고, 없는 재료는 일반 조미료(소금, 후추, 오일)만 추가 허용."""


def parse_recipe_text(text: str) -> tuple[str, str]:
    title = "AI 추천 레시피"
    for line in text.strip().splitlines():
        if line.startswith("제목:"):
            title = line.replace("제목:", "").strip()
            break
    return title, text.strip()


def generate_recipe(ingredients: list[str], api_key: str) -> tuple[str, str]:
    if not ingredients:
        raise ValueError("ingredients must not be empty")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = _PROMPT_TEMPLATE.format(ingredients=", ".join(ingredients))
    response = model.generate_content(prompt)
    return parse_recipe_text(response.text)
