# Phase 4: React Native 앱 설계

**날짜:** 2026-06-13
**상태:** 승인됨

---

## 개요

FastAPI 백엔드(Phase 2~3)와 연동하는 React Native 모바일 앱을 Expo Go 기반으로 구축한다.
카메라로 냉장고를 촬영하면 YOLO 식재료 인식 → Gemini 레시피 추천까지 한 흐름으로 동작하며,
히스토리 탭에서 과거 기록을 조회한다.

---

## 환경

- 프레임워크: React Native + Expo Go (로컬 테스트, 빌드 없음)
- 내비게이션: React Navigation v6 + Bottom Tabs
- 백엔드 주소: `.env`의 `API_URL` 환경변수로 관리 (예: `http://192.168.x.x:8000`)
- 언어: TypeScript

---

## 프로젝트 구조

```
FoodCameraApp/
├── .env                        # API_URL=http://192.168.x.x:8000
├── .env.example
├── App.tsx                     # NavigationContainer + Tab.Navigator 루트
├── src/
│   ├── api/
│   │   └── client.ts           # axios 인스턴스, API_URL 주입, 타임아웃 설정
│   ├── screens/
│   │   ├── CameraScreen.tsx    # 스캔 탭 메인 화면
│   │   └── HistoryScreen.tsx   # 히스토리 탭 메인 화면
│   ├── components/
│   │   ├── IngredientTag.tsx   # 식재료 칩 컴포넌트
│   │   ├── RecipeCard.tsx      # 레시피 카드 컴포넌트
│   │   └── LoadingOverlay.tsx  # 전체 화면 로딩 오버레이
│   └── types/
│       └── index.ts            # Ingredient, Recipe 공통 타입
├── app.json
└── package.json
```

---

## 탭 구성

| 탭 이름 | 아이콘 | 역할 |
|--------|--------|------|
| 스캔 | camera (Ionicons) | 사진 촬영/갤러리 선택 → 식재료 분석 → 레시피 생성 |
| 히스토리 | time (Ionicons) | 과거 식재료 및 레시피 기록 조회 |

---

## 화면 설계

### CameraScreen — 단계별 상태 머신

```
[idle]
  ↓ 촬영 버튼 or 갤러리 선택
[analyzing]  POST /analyze → LoadingOverlay "식재료 인식 중..."
  ↓ 성공
[ingredients]  식재료 태그 목록 + "레시피 추천받기" 버튼
  ↓ 버튼 탭
[generating]  POST /recipe → LoadingOverlay "레시피 생성 중..."
  ↓ 성공
[recipe]  RecipeCard 표시 + "다시 찍기" 버튼
  ↓ 버튼 탭
[idle]
```

- 상태 타입: `'idle' | 'analyzing' | 'ingredients' | 'generating' | 'recipe'`
- 에러 시 Alert로 메시지 표시 후 `idle`로 복귀
- 촬영과 갤러리 선택 모두 지원 (ActionSheet로 선택)

### HistoryScreen

- 상단 섹션: **식재료 기록** (`GET /ingredients`, 최신 20개)
  - 각 항목: 이름 + confidence % + 감지 시각
- 하단 섹션: **레시피 기록** (`GET /recipes`, 최신 10개)
  - 각 항목: 레시피 제목 + 사용 재료 태그 + 생성 시각
- `RefreshControl`로 당겨서 새로고침

---

## API 연동

### `POST /analyze`
- 입력: `multipart/form-data` — `file` 필드에 이미지
- 출력: `{ ingredients: [{ name: string, confidence: number }] }`

### `POST /recipe`
- 입력: `{ ingredients: string[] }`
- 출력: `{ title: string, content: string }`

### `GET /ingredients`
- 출력: `[{ id, name, confidence, detected_at }]`

### `GET /recipes`
- 출력: `[{ id, ingredients, title, content, created_at }]` (배열 직접 반환)

---

## 디자인 시스템

| 토큰 | 값 |
|------|-----|
| 배경 | `#0F0F0F` |
| 카드 배경 | `#1C1C1E` |
| 액센트 | `#A8E063` (라임 그린) |
| 텍스트 주 | `#FFFFFF` |
| 텍스트 부 | `#8E8E93` |
| 카드 radius | `16` |
| 패딩 기본 | `16` |

- 폰트: 시스템 폰트 (`System`), 제목 `fontWeight: '700'`
- 식재료 태그: 라임 그린 배경 + `#0F0F0F` 텍스트, `borderRadius: 20`
- 탭 바: 다크 배경, 활성 탭 액센트 색상

---

## 의존성

```json
{
  "expo": "~51.x",
  "react-native": "0.74.x",
  "@react-navigation/native": "^6",
  "@react-navigation/bottom-tabs": "^6",
  "react-native-screens": "^3",
  "react-native-safe-area-context": "^4",
  "expo-camera": "^15",
  "expo-image-picker": "^15",
  "axios": "^1",
  "react-native-dotenv": "^3",
  "@expo/vector-icons": "^14"
}
```

---

## 환경변수 (.env)

```
API_URL=http://192.168.x.x:8000
```

- `.env`는 `.gitignore`에 추가
- `.env.example`에 키 없는 템플릿 커밋

---

## 에러 처리

- 네트워크 오류: Alert "서버에 연결할 수 없습니다. API_URL을 확인해주세요."
- 식재료 미감지: Alert "식재료를 인식하지 못했습니다. 다시 시도해주세요."
- 레시피 생성 실패: Alert "레시피 생성에 실패했습니다."
- 모든 에러 후 `idle` 상태로 복귀

---

## 테스트 방법

1. `cd FoodCameraApp && npx expo start`
2. Expo Go 앱으로 QR 스캔
3. `.env`에 Mac IP 주소 입력 후 재시작
4. 스캔 탭: 사과 사진 촬영 → 식재료 인식 → 레시피 확인
5. 히스토리 탭: 저장된 기록 조회 및 새로고침 확인
