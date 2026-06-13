# Phase 2 & 3: FastAPI 백엔드 + LLM 통합 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI 서버를 구축하여 YOLO 식재료 인식, Supabase 저장, Gemini 레시피 생성을 통합한다.

**Architecture:** YOLO 모델은 서버 시작 시 MPS로 1회 로드하여 `app.state.model`에 보관한다. 각 요청은 라우터 → 서비스 레이어를 거치며, 외부 의존성(Supabase, Gemini)은 서비스 모듈로 격리한다.

**Tech Stack:** FastAPI, Uvicorn, Ultralytics (YOLOv8), Supabase Python SDK v2, google-generativeai, Pillow, pytest, httpx

---

## 파일 구조

```
Food_Camera/
├── weights/best.pt                        # 기존 (변경 없음)
├── app/
│   ├── __init__.py
│   ├── main.py                            # 생성: FastAPI 앱 + lifespan
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── analyze.py                     # 생성: POST /analyze
│   │   ├── recipe.py                      # 생성: POST /recipe
│   │   └── data.py                        # 생성: GET /ingredients, GET /recipes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── yolo.py                        # 생성: YOLO 추론 로직
│   │   ├── gemini.py                      # 생성: Gemini API 호출
│   │   └── supabase_client.py             # 생성: Supabase CRUD
│   └── models/
│       ├── __init__.py
│       └── schemas.py                     # 생성: Pydantic 스키마
├── tests/
│   ├── __init__.py
│   ├── test_schemas.py
│   ├── test_yolo_service.py
│   ├── test_supabase_service.py
│   ├── test_gemini_service.py
│   ├── test_analyze_router.py
│   ├── test_recipe_router.py
│   └── test_data_router.py
├── .env                                   # 생성: 실제 키 (gitignore)
├── .env.example                           # 생성: 키 없는 템플릿
├── .gitignore                             # 생성
└── requirements.txt                       # 생성
```

---

## Task 1: 프로젝트 스캐폴딩

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.env`
- Create: `.gitignore`
- Create: `app/__init__.py`, `app/routers/__init__.py`, `app/services/__init__.py`, `app/models/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: 디렉터리 및 `__init__.py` 생성**

```bash
mkdir -p app/routers app/services app/models tests
touch app/__init__.py app/routers/__init__.py app/services/__init__.py app/models/__init__.py tests/__init__.py
```

- [ ] **Step 2: `requirements.txt` 작성**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
ultralytics==8.3.0
python-multipart==0.0.12
supabase==2.7.4
google-generativeai==0.8.3
python-dotenv==1.0.1
Pillow==10.4.0
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
```

- [ ] **Step 3: `.env.example` 작성**

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GEMINI_API_KEY=your-gemini-key
MODEL_PATH=weights/best.pt
```

- [ ] **Step 4: `.env` 작성** (실제 값 입력)

```
SUPABASE_URL=https://cqrdannjexkazagqfoho.supabase.co
SUPABASE_KEY=<your-supabase-anon-key>
GEMINI_API_KEY=<발급받은_Gemini_API_키_입력>
MODEL_PATH=weights/best.pt
```

- [ ] **Step 5: `.gitignore` 작성**

```
.env
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
.DS_Store
```

- [ ] **Step 6: 의존성 설치**

```bash
pip install -r requirements.txt
```

Expected: 설치 완료, 에러 없음

- [ ] **Step 7: 커밋**

```bash
git add requirements.txt .env.example .gitignore app/ tests/
git commit -m "feat: scaffold project structure"
```

---

## Task 2: Pydantic 스키마

**Files:**
- Create: `app/models/schemas.py`
- Create: `tests/test_schemas.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_schemas.py`:
```python
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
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_schemas.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.models.schemas'`

- [ ] **Step 3: `app/models/schemas.py` 구현**

```python
from pydantic import BaseModel, field_validator
from typing import Optional
import uuid
from datetime import datetime


class DetectedIngredient(BaseModel):
    name: str
    confidence: float


class AnalyzeResponse(BaseModel):
    ingredients: list[DetectedIngredient]


class RecipeRequest(BaseModel):
    ingredients: list[str]

    @field_validator("ingredients")
    @classmethod
    def ingredients_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("ingredients must not be empty")
        return v


class RecipeResponse(BaseModel):
    title: str
    content: str


class IngredientRecord(BaseModel):
    id: Optional[str] = None
    name: str
    confidence: float
    detected_at: Optional[str] = None


class RecipeRecord(BaseModel):
    id: Optional[str] = None
    ingredients: list[str]
    title: str
    content: str
    created_at: Optional[str] = None
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_schemas.py -v
```

Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add app/models/schemas.py tests/test_schemas.py
git commit -m "feat: add pydantic schemas"
```

---

## Task 3: YOLO 서비스

**Files:**
- Create: `app/services/yolo.py`
- Create: `tests/test_yolo_service.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_yolo_service.py`:
```python
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
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_yolo_service.py -v
```

Expected: `ImportError: cannot import name 'run_inference'`

- [ ] **Step 3: `app/services/yolo.py` 구현**

```python
import io
from PIL import Image
from app.models.schemas import DetectedIngredient


def run_inference(model, image_bytes: bytes) -> list[DetectedIngredient]:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = model(img)

    best: dict[str, float] = {}
    for result in results:
        cls_list = result.boxes.cls.tolist()
        conf_list = result.boxes.conf.tolist()
        for cls_idx, conf in zip(cls_list, conf_list):
            if conf < 0.5:
                continue
            name = result.names[int(cls_idx)]
            if name not in best or conf > best[name]:
                best[name] = conf

    return [DetectedIngredient(name=name, confidence=conf) for name, conf in best.items()]


def load_model(model_path: str):
    from ultralytics import YOLO
    import torch
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = YOLO(model_path)
    model.to(device)
    return model
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_yolo_service.py -v
```

Expected: 4 passed

- [ ] **Step 5: 커밋**

```bash
git add app/services/yolo.py tests/test_yolo_service.py
git commit -m "feat: add yolo inference service"
```

---

## Task 4: Supabase 서비스

**Files:**
- Create: `app/services/supabase_client.py`
- Create: `tests/test_supabase_service.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_supabase_service.py`:
```python
from unittest.mock import MagicMock
from app.services.supabase_client import save_ingredients, save_recipe, get_ingredients, get_recipes
from app.models.schemas import DetectedIngredient, RecipeResponse


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
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_supabase_service.py -v
```

Expected: `ImportError: cannot import name 'save_ingredients'`

- [ ] **Step 3: `app/services/supabase_client.py` 구현**

```python
import os
from supabase import create_client, Client
from app.models.schemas import DetectedIngredient


def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def save_ingredients(client: Client, ingredients: list[DetectedIngredient]) -> None:
    rows = [{"name": i.name, "confidence": i.confidence} for i in ingredients]
    client.table("ingredients").insert(rows).execute()


def save_recipe(client: Client, ingredients: list[str], title: str, content: str) -> None:
    client.table("recipes").insert({
        "ingredients": ingredients,
        "title": title,
        "content": content,
    }).execute()


def get_ingredients(client: Client) -> list[dict]:
    result = (
        client.table("ingredients")
        .select("*")
        .order("detected_at", desc=True)
        .limit(20)
        .execute()
    )
    return result.data


def get_recipes(client: Client) -> list[dict]:
    result = (
        client.table("recipes")
        .select("*")
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    return result.data
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_supabase_service.py -v
```

Expected: 4 passed

- [ ] **Step 5: 커밋**

```bash
git add app/services/supabase_client.py tests/test_supabase_service.py
git commit -m "feat: add supabase crud service"
```

---

## Task 5: Gemini 서비스

**Files:**
- Create: `app/services/gemini.py`
- Create: `tests/test_gemini_service.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_gemini_service.py`:
```python
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
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_gemini_service.py -v
```

Expected: `ImportError: cannot import name 'generate_recipe'`

- [ ] **Step 3: `app/services/gemini.py` 구현**

```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_gemini_service.py -v
```

Expected: 4 passed

- [ ] **Step 5: 커밋**

```bash
git add app/services/gemini.py tests/test_gemini_service.py
git commit -m "feat: add gemini recipe generation service"
```

---

## Task 6: /analyze 라우터

**Files:**
- Create: `app/routers/analyze.py`
- Create: `tests/test_analyze_router.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_analyze_router.py`:
```python
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
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_analyze_router.py -v
```

Expected: `ImportError: cannot import name 'router'`

- [ ] **Step 3: `app/routers/analyze.py` 구현**

```python
from fastapi import APIRouter, UploadFile, File, Request
from app.models.schemas import AnalyzeResponse
from app.services.yolo import run_inference
from app.services.supabase_client import get_client, save_ingredients

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(request: Request, file: UploadFile = File(...)):
    image_bytes = await file.read()
    model = request.app.state.model
    ingredients = run_inference(model, image_bytes)

    if ingredients:
        db = get_client()
        save_ingredients(db, ingredients)

    return AnalyzeResponse(ingredients=ingredients)
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_analyze_router.py -v
```

Expected: 2 passed

- [ ] **Step 5: 커밋**

```bash
git add app/routers/analyze.py tests/test_analyze_router.py
git commit -m "feat: add /analyze endpoint"
```

---

## Task 7: /recipe 라우터

**Files:**
- Create: `app/routers/recipe.py`
- Create: `tests/test_recipe_router.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_recipe_router.py`:
```python
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
         patch("app.routers.recipe.get_client"):

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
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_recipe_router.py -v
```

Expected: `ImportError: cannot import name 'router'`

- [ ] **Step 3: `app/routers/recipe.py` 구현**

```python
import os
from fastapi import APIRouter
from app.models.schemas import RecipeRequest, RecipeResponse
from app.services.gemini import generate_recipe
from app.services.supabase_client import get_client, save_recipe

router = APIRouter()


@router.post("/recipe", response_model=RecipeResponse)
async def create_recipe(body: RecipeRequest):
    api_key = os.environ["GEMINI_API_KEY"]
    title, content = generate_recipe(body.ingredients, api_key=api_key)

    db = get_client()
    save_recipe(db, body.ingredients, title, content)

    return RecipeResponse(title=title, content=content)
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_recipe_router.py -v
```

Expected: 2 passed

- [ ] **Step 5: 커밋**

```bash
git add app/routers/recipe.py tests/test_recipe_router.py
git commit -m "feat: add /recipe endpoint"
```

---

## Task 8: /ingredients, /recipes 라우터

**Files:**
- Create: `app/routers/data.py`
- Create: `tests/test_data_router.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_data_router.py`:
```python
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
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_data_router.py -v
```

Expected: `ImportError: cannot import name 'router'`

- [ ] **Step 3: `app/routers/data.py` 구현**

```python
from fastapi import APIRouter
from app.services.supabase_client import get_client, get_ingredients, get_recipes

router = APIRouter()


@router.get("/ingredients")
async def list_ingredients():
    db = get_client()
    return get_ingredients(db)


@router.get("/recipes")
async def list_recipes():
    db = get_client()
    return get_recipes(db)
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_data_router.py -v
```

Expected: 2 passed

- [ ] **Step 5: 커밋**

```bash
git add app/routers/data.py tests/test_data_router.py
git commit -m "feat: add /ingredients and /recipes GET endpoints"
```

---

## Task 9: FastAPI 메인 앱 (lifespan)

**Files:**
- Create: `app/main.py`

- [ ] **Step 1: `app/main.py` 작성**

```python
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analyze, recipe, data
from app.services.yolo import load_model

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = os.environ.get("MODEL_PATH", "weights/best.pt")
    app.state.model = load_model(model_path)
    print(f"[startup] YOLO model loaded from {model_path}")
    yield
    print("[shutdown] server stopped")


app = FastAPI(title="Food Camera API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(recipe.router)
app.include_router(data.router)
```

- [ ] **Step 2: 전체 테스트 통과 확인**

```bash
pytest tests/ -v
```

Expected: 모든 테스트 pass (15개 이상)

- [ ] **Step 3: 서버 기동 확인**

```bash
uvicorn app.main:app --reload
```

Expected 출력:
```
[startup] YOLO model loaded from weights/best.pt
INFO:     Uvicorn running on http://127.0.0.1:8000
```

- [ ] **Step 4: 커밋**

```bash
git add app/main.py
git commit -m "feat: add fastapi app with lifespan model loading"
```

---

## Task 10: Supabase 테이블 생성

**Files:** Supabase 대시보드에서 SQL 실행 (로컬 파일 없음)

- [ ] **Step 1: Supabase 대시보드 접속**

[https://supabase.com/dashboard/project/cqrdannjexkazagqfoho](https://supabase.com/dashboard/project/cqrdannjexkazagqfoho) → **SQL Editor** 탭

- [ ] **Step 2: `ingredients` 테이블 생성**

```sql
create table if not exists ingredients (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  confidence  float not null,
  detected_at timestamptz not null default now()
);
```

실행 후 "Success" 메시지 확인

- [ ] **Step 3: `recipes` 테이블 생성**

```sql
create table if not exists recipes (
  id          uuid primary key default gen_random_uuid(),
  ingredients text[] not null,
  title       text not null,
  content     text not null,
  created_at  timestamptz not null default now()
);
```

실행 후 "Success" 메시지 확인

- [ ] **Step 4: 연결 테스트**

서버가 실행 중인 상태에서:

```bash
curl -X POST http://localhost:8000/recipe \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["Apple"]}'
```

Expected: `{"title": "...", "content": "..."}` 형태의 JSON 응답 (Gemini API 키가 설정된 경우)

---

## Task 11: Swagger UI 통합 테스트

서버 실행 후 `http://localhost:8000/docs`에서 순서대로 실행:

- [ ] **Step 1: `/analyze` 테스트**

사과 이미지 파일 업로드 → `{"ingredients": [{"name": "Apple", "confidence": 0.XX}]}` 응답 확인

- [ ] **Step 2: Supabase `ingredients` 저장 확인**

Supabase 대시보드 → Table Editor → `ingredients` 테이블에 레코드 삽입 확인

- [ ] **Step 3: `/recipe` 테스트**

`{"ingredients": ["Apple"]}` 전송 → 한국어 레시피 응답 확인

- [ ] **Step 4: Supabase `recipes` 저장 확인**

Supabase 대시보드 → `recipes` 테이블에 레코드 삽입 확인

- [ ] **Step 5: `/ingredients` 테스트**

GET 요청 → 저장된 식재료 목록 반환 확인

- [ ] **Step 6: `/recipes` 테스트**

GET 요청 → 저장된 레시피 목록 반환 확인

- [ ] **Step 7: 최종 커밋**

```bash
git add .
git commit -m "feat: phase 2 & 3 backend complete"
```

---

## 체크리스트 요약

- [ ] Task 1: 프로젝트 스캐폴딩 완료
- [ ] Task 2: Pydantic 스키마 (5 tests pass)
- [ ] Task 3: YOLO 서비스 (4 tests pass)
- [ ] Task 4: Supabase 서비스 (4 tests pass)
- [ ] Task 5: Gemini 서비스 (4 tests pass)
- [ ] Task 6: /analyze 라우터 (2 tests pass)
- [ ] Task 7: /recipe 라우터 (2 tests pass)
- [ ] Task 8: /ingredients, /recipes 라우터 (2 tests pass)
- [ ] Task 9: FastAPI main.py — 전체 15+ tests pass, 서버 기동 확인
- [ ] Task 10: Supabase 테이블 생성 완료
- [ ] Task 11: Swagger UI 통합 테스트 전 엔드포인트 통과
