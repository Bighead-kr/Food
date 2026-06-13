# Phase 2 & 3: FastAPI 백엔드 + LLM 통합 설계

**날짜:** 2026-06-13  
**상태:** 승인됨

---

## 개요

냉장고 식재료 인식 및 AI 레시피 추천 앱의 백엔드 서버를 FastAPI로 구축한다.
YOLO 모델(best.pt)을 서버 시작 시 MPS로 로드하고, Supabase에 결과를 저장하며, Gemini API로 레시피를 생성한다.
클라이언트는 React Native이며 배포 없이 로컬 테스트 수준으로 완성한다.

---

## 환경

- 플랫폼: M4 Mac (Apple Silicon, MPS)
- Python: 3.11+
- 모델: YOLOv8n (`weights/best.pt`), 클래스: `{0: 'Apple'}`
- DB: Supabase (PostgreSQL)
- LLM: Gemini API (gemini-2.0-flash)
- 클라이언트: React Native (로컬 테스트)

---

## 프로젝트 구조

```
Food_Camera/
├── weights/
│   └── best.pt
├── app/
│   ├── main.py              # FastAPI 앱 엔트리포인트, lifespan 모델 로딩
│   ├── routers/
│   │   ├── analyze.py       # POST /analyze — 이미지 → 식재료 리스트
│   │   ├── recipe.py        # POST /recipe  — 식재료 → 레시피 생성
│   │   └── data.py          # GET  /ingredients, GET /recipes
│   ├── services/
│   │   ├── yolo.py          # YOLO 추론 (MPS), 결과 파싱
│   │   ├── gemini.py        # Gemini API 호출, 프롬프트 템플릿
│   │   └── supabase_client.py  # Supabase insert/select
│   └── models/
│       └── schemas.py       # Pydantic 요청/응답 스키마
├── .env                     # SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY
├── .env.example             # 키 없는 템플릿 (커밋용)
├── .gitignore               # .env 포함
└── requirements.txt
```

---

## API 엔드포인트

### `POST /analyze`
- **입력:** `multipart/form-data` — 이미지 파일
- **처리:** YOLO 추론 → 감지된 클래스 + confidence 추출 → Supabase `ingredients` 저장
- **출력:**
  ```json
  {
    "ingredients": [
      {"name": "Apple", "confidence": 0.91}
    ]
  }
  ```

### `POST /recipe`
- **입력:** `application/json`
  ```json
  {"ingredients": ["Apple"]}
  ```
- **처리:** Gemini API에 프롬프트 전송 → 레시피 생성 → Supabase `recipes` 저장
- **출력:**
  ```json
  {
    "title": "사과 샐러드",
    "content": "재료: ...\n조리법: ..."
  }
  ```

### `GET /ingredients`
- **출력:** Supabase `ingredients` 테이블 전체 조회 (최신순 20개)

### `GET /recipes`
- **출력:** Supabase `recipes` 테이블 전체 조회 (최신순 10개)

---

## Supabase 테이블 스키마

### `ingredients`
```sql
create table ingredients (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  confidence  float not null,
  detected_at timestamptz not null default now()
);
```

### `recipes`
```sql
create table recipes (
  id          uuid primary key default gen_random_uuid(),
  ingredients text[] not null,
  title       text not null,
  content     text not null,
  created_at  timestamptz not null default now()
);
```

---

## YOLO 서비스 (services/yolo.py)

- 서버 시작 시 `lifespan`으로 모델 1회 로드 (`device="mps"`)
- `app.state.model`에 저장하여 요청마다 재로드 방지
- `conf=0.5` 이상인 감지 결과만 반환
- 동일 이미지에서 중복 클래스 감지 시 confidence 최고값 1개만 반환

---

## Gemini 서비스 (services/gemini.py)

**프롬프트 템플릿:**
```
다음 재료를 사용한 간단한 레시피를 한국어로 추천해줘.
재료: {ingredients}

형식:
제목: [레시피 이름]
재료: [목록]
조리법: [단계별 설명]
주의: 주어진 재료만 사용하고, 없는 재료는 일반 조미료(소금, 후추, 오일)만 추가 허용.
```

- 모델: `gemini-2.0-flash`
- 재료 리스트가 비어있으면 API 호출 없이 에러 반환

---

## 환경변수 (.env)

```
SUPABASE_URL=https://cqrdannjexkazagqfoho.supabase.co
SUPABASE_KEY=<your-supabase-anon-key>
GEMINI_API_KEY=<gemini_key>
MODEL_PATH=weights/best.pt
```

---

## 의존성 (requirements.txt)

```
fastapi
uvicorn[standard]
ultralytics
python-multipart
supabase
google-generativeai
python-dotenv
Pillow
```

---

## 테스트 방법

1. `uvicorn app.main:app --reload` 실행
2. `http://localhost:8000/docs` Swagger UI에서 각 엔드포인트 수동 테스트
3. `/analyze`에 사과 이미지 업로드 → 응답 확인
4. `/recipe`에 `["Apple"]` 전송 → 레시피 확인
5. Supabase 대시보드에서 데이터 저장 확인

---

## 체크리스트

- [ ] FastAPI 앱 구조 생성 및 lifespan 모델 로딩 확인
- [ ] `/analyze` 엔드포인트 — YOLO 추론 동작
- [ ] Supabase 테이블 생성 및 insert/select 동작
- [ ] `/recipe` 엔드포인트 — Gemini 레시피 생성 동작
- [ ] `/ingredients`, `/recipes` GET 엔드포인트 동작
- [ ] `.env` 설정 및 `.gitignore` 적용
- [ ] Swagger UI 전체 엔드포인트 수동 테스트 통과
