# Phase 4: React Native App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expo Go 기반 React Native 앱으로 냉장고 사진 → 식재료 인식 → 레시피 생성 흐름을 구현하고, 히스토리 탭에서 과거 기록을 조회한다.

**Architecture:** React Navigation Bottom Tabs로 스캔/히스토리 두 탭을 구성한다. CameraScreen은 `idle → analyzing → ingredients → generating → recipe` 상태 머신으로 동작하며, API 호출은 axios 인스턴스를 통해 `.env`의 `API_URL`로 전송한다.

**Tech Stack:** Expo SDK (latest), React Native, TypeScript, React Navigation v6 + Bottom Tabs, expo-image-picker, axios, react-native-dotenv, @expo/vector-icons

---

## 파일 구조

```
/Users/jung/Desktop/Develop/FoodCameraApp/
├── .env                          # API_URL=http://<MAC_IP>:8000
├── .env.example                  # API_URL=http://192.168.x.x:8000
├── .gitignore
├── app.json
├── babel.config.js               # react-native-dotenv 플러그인 추가
├── App.tsx                       # NavigationContainer + Tab.Navigator
├── src/
│   ├── types/
│   │   ├── index.ts              # Ingredient, Recipe 타입
│   │   └── env.d.ts              # @env 모듈 타입 선언
│   ├── api/
│   │   └── client.ts             # axios 인스턴스 + 4개 API 함수
│   ├── components/
│   │   ├── LoadingOverlay.tsx    # 메시지 순환 로딩 화면
│   │   ├── IngredientTag.tsx     # 라임 칩 컴포넌트
│   │   └── RecipeCard.tsx        # 레시피 카드
│   └── screens/
│       ├── CameraScreen.tsx      # 스캔 탭 — 상태 머신
│       └── HistoryScreen.tsx     # 히스토리 탭 — 목록 조회
└── package.json
```

---

## Task 1: 프로젝트 스캐폴딩 및 의존성 설치

**Files:**
- Create: `/Users/jung/Desktop/Develop/FoodCameraApp/` (전체 프로젝트)
- Modify: `babel.config.js`

- [ ] **Step 1: Expo 프로젝트 생성**

```bash
cd /Users/jung/Desktop/Develop
npx create-expo-app@latest FoodCameraApp --template blank-typescript
cd FoodCameraApp
```

Expected: `FoodCameraApp/` 디렉토리 생성, `App.tsx`, `package.json` 등 기본 파일 생성됨

- [ ] **Step 2: 의존성 설치**

```bash
npx expo install expo-image-picker expo-camera
npx expo install react-native-screens react-native-safe-area-context
npm install @react-navigation/native @react-navigation/bottom-tabs
npm install axios react-native-dotenv
npx expo install @expo/vector-icons
```

Expected: `node_modules/` 업데이트, 에러 없음

- [ ] **Step 3: babel.config.js에 react-native-dotenv 플러그인 추가**

`babel.config.js` 전체를 다음으로 교체:

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      ['module:react-native-dotenv', {
        moduleName: '@env',
        path: '.env',
        safe: false,
        allowUndefined: true,
      }],
    ],
  };
};
```

- [ ] **Step 4: .env 및 .env.example 생성**

`.env`:
```
API_URL=http://192.168.x.x:8000
```
> **주의:** Mac의 실제 IP로 교체 필요. `ifconfig | grep "inet " | grep -v 127.0.0.1`로 확인

`.env.example`:
```
API_URL=http://192.168.x.x:8000
```

- [ ] **Step 5: .gitignore에 .env 추가**

`.gitignore` 파일에 다음 줄 추가 (이미 있으면 skip):
```
.env
```

- [ ] **Step 6: 동작 확인**

```bash
npx expo start
```

Expected: QR 코드가 터미널에 출력됨, Metro Bundler 시작

- [ ] **Step 7: 커밋**

```bash
git init
git add -A
git commit -m "feat: scaffold expo project with dependencies"
```

---

## Task 2: 타입 및 환경변수 모듈 정의

**Files:**
- Create: `src/types/index.ts`
- Create: `src/types/env.d.ts`

- [ ] **Step 1: src/types 디렉토리 생성 후 index.ts 작성**

`src/types/index.ts`:
```ts
export interface Ingredient {
  id?: string;
  name: string;
  confidence: number;
  detected_at?: string;
}

export interface Recipe {
  id?: string;
  ingredients?: string[];
  title: string;
  content: string;
  created_at?: string;
}
```

- [ ] **Step 2: @env 모듈 타입 선언 파일 작성**

`src/types/env.d.ts`:
```ts
declare module '@env' {
  export const API_URL: string;
}
```

- [ ] **Step 3: 커밋**

```bash
git add src/types/
git commit -m "feat: add Ingredient and Recipe types"
```

---

## Task 3: API 클라이언트 구현

**Files:**
- Create: `src/api/client.ts`
- Test: Jest mock으로 axios 호출 검증

- [ ] **Step 1: 테스트 파일 작성**

`src/api/__tests__/client.test.ts`:
```ts
jest.mock('axios', () => ({
  create: () => ({
    post: jest.fn(),
    get: jest.fn(),
  }),
}));

import axios from 'axios';

// axios.create()의 반환 인스턴스를 mock
const mockHttp = axios.create() as jest.Mocked<ReturnType<typeof axios.create>>;

describe('API client', () => {
  it('generateRecipe sends ingredients array', async () => {
    (mockHttp.post as jest.Mock).mockResolvedValueOnce({
      data: { title: '사과 샐러드', content: '조리법...' },
    });

    // 실제 import는 mock 이후에
    const { generateRecipe } = await import('../client');
    const result = await generateRecipe(['Apple']);

    expect(mockHttp.post).toHaveBeenCalledWith('/recipe', { ingredients: ['Apple'] });
    expect(result.title).toBe('사과 샐러드');
  });

  it('fetchIngredients returns array', async () => {
    (mockHttp.get as jest.Mock).mockResolvedValueOnce({
      data: [{ id: '1', name: 'Apple', confidence: 0.91 }],
    });

    const { fetchIngredients } = await import('../client');
    const result = await fetchIngredients();

    expect(mockHttp.get).toHaveBeenCalledWith('/ingredients');
    expect(result[0].name).toBe('Apple');
  });
});
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
npx jest src/api/__tests__/client.test.ts
```

Expected: FAIL — `client.ts` 없음

- [ ] **Step 3: client.ts 구현**

`src/api/client.ts`:
```ts
import axios from 'axios';
import { API_URL } from '@env';
import { Ingredient, Recipe } from '../types';

const http = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

export async function analyzeImage(uri: string): Promise<{ ingredients: Ingredient[] }> {
  const form = new FormData();
  form.append('file', { uri, type: 'image/jpeg', name: 'photo.jpg' } as any);
  const { data } = await http.post('/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function generateRecipe(ingredients: string[]): Promise<Recipe> {
  const { data } = await http.post('/recipe', { ingredients });
  return data;
}

export async function fetchIngredients(): Promise<Ingredient[]> {
  const { data } = await http.get('/ingredients');
  return data;
}

export async function fetchRecipes(): Promise<Recipe[]> {
  const { data } = await http.get('/recipes');
  return data;
}
```

- [ ] **Step 4: 테스트 실행 (통과 확인)**

```bash
npx jest src/api/__tests__/client.test.ts
```

Expected: PASS (2 tests)

- [ ] **Step 5: 커밋**

```bash
git add src/api/
git commit -m "feat: add API client with axios"
```

---

## Task 4: LoadingOverlay 컴포넌트

**Files:**
- Create: `src/components/LoadingOverlay.tsx`

- [ ] **Step 1: LoadingOverlay.tsx 작성**

`src/components/LoadingOverlay.tsx`:
```tsx
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';

interface Props {
  messages: string[];
}

export default function LoadingOverlay({ messages }: Props) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setIndex(prev => (prev + 1) % messages.length);
    }, 1800);
    return () => clearInterval(id);
  }, [messages]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#A8E063" />
      <Text style={styles.message}>{messages[index]}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F0F0F',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  message: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginTop: 20,
    textAlign: 'center',
  },
});
```

- [ ] **Step 2: 커밋**

```bash
git add src/components/LoadingOverlay.tsx
git commit -m "feat: add LoadingOverlay with cycling messages"
```

---

## Task 5: IngredientTag 컴포넌트

**Files:**
- Create: `src/components/IngredientTag.tsx`

- [ ] **Step 1: IngredientTag.tsx 작성**

`src/components/IngredientTag.tsx`:
```tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ingredient } from '../types';

interface Props {
  ingredient: Ingredient;
}

export default function IngredientTag({ ingredient }: Props) {
  return (
    <View style={styles.tag}>
      <Text style={styles.name}>{ingredient.name}</Text>
      <Text style={styles.confidence}>{Math.round(ingredient.confidence * 100)}%</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  tag: {
    backgroundColor: '#A8E063',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    margin: 4,
  },
  name: { color: '#0F0F0F', fontWeight: '700', fontSize: 14 },
  confidence: { color: '#2D4A0A', fontSize: 12 },
});
```

- [ ] **Step 2: 커밋**

```bash
git add src/components/IngredientTag.tsx
git commit -m "feat: add IngredientTag chip component"
```

---

## Task 6: RecipeCard 컴포넌트

**Files:**
- Create: `src/components/RecipeCard.tsx`

- [ ] **Step 1: RecipeCard.tsx 작성**

`src/components/RecipeCard.tsx`:
```tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Recipe } from '../types';

interface Props {
  recipe: Recipe;
}

export default function RecipeCard({ recipe }: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{recipe.title}</Text>
      <Text style={styles.content}>{recipe.content}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1C1C1E',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
  },
  title: {
    color: '#A8E063',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 12,
  },
  content: {
    color: '#FFFFFF',
    fontSize: 15,
    lineHeight: 24,
  },
});
```

- [ ] **Step 2: 커밋**

```bash
git add src/components/RecipeCard.tsx
git commit -m "feat: add RecipeCard component"
```

---

## Task 7: CameraScreen 구현

**Files:**
- Create: `src/screens/CameraScreen.tsx`

- [ ] **Step 1: CameraScreen.tsx 작성**

`src/screens/CameraScreen.tsx`:
```tsx
import React, { useState } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity,
  Image, ScrollView, Alert, Platform, ActionSheetIOS,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { analyzeImage, generateRecipe } from '../api/client';
import { Ingredient, Recipe } from '../types';
import IngredientTag from '../components/IngredientTag';
import RecipeCard from '../components/RecipeCard';
import LoadingOverlay from '../components/LoadingOverlay';

type ScreenState = 'idle' | 'analyzing' | 'ingredients' | 'generating' | 'recipe';

const ANALYZING_MESSAGES = [
  '컴퓨터 비전으로 분석 중...',
  '딥러닝 기반 식재료 분석 중...',
];

const GENERATING_MESSAGES = [
  'AI가 레시피를 생성 중...',
  '맞춤 레시피를 준비 중...',
];

export default function CameraScreen() {
  const [state, setState] = useState<ScreenState>('idle');
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [recipe, setRecipe] = useState<Recipe | null>(null);

  const pickImage = async (useCamera: boolean) => {
    const perm = useCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!perm.granted) {
      Alert.alert('권한 필요', '사진 접근 권한이 필요합니다.');
      return;
    }

    const result = useCamera
      ? await ImagePicker.launchCameraAsync({ quality: 0.8 })
      : await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });

    if (!result.canceled && result.assets[0]) {
      const uri = result.assets[0].uri;
      setImageUri(uri);
      await analyze(uri);
    }
  };

  const handleSelectSource = () => {
    if (Platform.OS === 'ios') {
      ActionSheetIOS.showActionSheetWithOptions(
        { options: ['취소', '카메라로 촬영', '갤러리에서 선택'], cancelButtonIndex: 0 },
        (idx) => {
          if (idx === 1) pickImage(true);
          else if (idx === 2) pickImage(false);
        },
      );
    } else {
      Alert.alert('사진 선택', '', [
        { text: '카메라로 촬영', onPress: () => pickImage(true) },
        { text: '갤러리에서 선택', onPress: () => pickImage(false) },
        { text: '취소', style: 'cancel' },
      ]);
    }
  };

  const analyze = async (uri: string) => {
    setState('analyzing');
    try {
      const result = await analyzeImage(uri);
      if (result.ingredients.length === 0) {
        Alert.alert('인식 실패', '식재료를 인식하지 못했습니다. 다시 시도해주세요.');
        setState('idle');
        return;
      }
      setIngredients(result.ingredients);
      setState('ingredients');
    } catch {
      Alert.alert('연결 오류', '서버에 연결할 수 없습니다. .env의 API_URL을 확인해주세요.');
      setState('idle');
    }
  };

  const getRecipe = async () => {
    setState('generating');
    try {
      const result = await generateRecipe(ingredients.map(i => i.name));
      setRecipe(result);
      setState('recipe');
    } catch {
      Alert.alert('오류', '레시피 생성에 실패했습니다.');
      setState('ingredients');
    }
  };

  const reset = () => {
    setState('idle');
    setImageUri(null);
    setIngredients([]);
    setRecipe(null);
  };

  if (state === 'analyzing') return <LoadingOverlay messages={ANALYZING_MESSAGES} />;
  if (state === 'generating') return <LoadingOverlay messages={GENERATING_MESSAGES} />;

  if (state === 'idle') {
    return (
      <View style={styles.container}>
        <View style={styles.placeholder}>
          <Text style={styles.placeholderIcon}>📷</Text>
          <Text style={styles.placeholderText}>냉장고를 촬영해보세요</Text>
          <Text style={styles.placeholderSub}>식재료를 자동으로 인식합니다</Text>
        </View>
        <TouchableOpacity style={styles.primaryButton} onPress={handleSelectSource}>
          <Text style={styles.primaryButtonText}>사진 찍기 / 선택</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (state === 'ingredients') {
    return (
      <ScrollView style={styles.scrollContainer} contentContainerStyle={styles.scrollContent}>
        {imageUri && <Image source={{ uri: imageUri }} style={styles.preview} />}
        <Text style={styles.sectionTitle}>인식된 식재료</Text>
        <View style={styles.tagContainer}>
          {ingredients.map(i => <IngredientTag key={i.name} ingredient={i} />)}
        </View>
        <TouchableOpacity style={styles.primaryButton} onPress={getRecipe}>
          <Text style={styles.primaryButtonText}>레시피 추천받기</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryButton} onPress={reset}>
          <Text style={styles.secondaryButtonText}>다시 찍기</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  }

  // state === 'recipe'
  return (
    <ScrollView style={styles.scrollContainer} contentContainerStyle={styles.scrollContent}>
      {recipe && <RecipeCard recipe={recipe} />}
      <TouchableOpacity style={styles.primaryButton} onPress={reset}>
        <Text style={styles.primaryButtonText}>다시 찍기</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1, backgroundColor: '#0F0F0F', padding: 16, justifyContent: 'space-between',
  },
  scrollContainer: { flex: 1, backgroundColor: '#0F0F0F' },
  scrollContent: { padding: 16, paddingBottom: 32 },
  placeholder: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 8 },
  placeholderIcon: { fontSize: 72, marginBottom: 8 },
  placeholderText: { color: '#FFFFFF', fontSize: 20, fontWeight: '700' },
  placeholderSub: { color: '#8E8E93', fontSize: 14 },
  preview: { width: '100%', height: 220, borderRadius: 16, marginBottom: 20 },
  sectionTitle: { color: '#FFFFFF', fontSize: 18, fontWeight: '700', marginBottom: 12 },
  tagContainer: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 24 },
  primaryButton: {
    backgroundColor: '#A8E063', borderRadius: 14, padding: 16,
    alignItems: 'center', marginBottom: 12,
  },
  primaryButtonText: { color: '#0F0F0F', fontSize: 16, fontWeight: '700' },
  secondaryButton: {
    borderWidth: 1, borderColor: '#3A3A3C', borderRadius: 14,
    padding: 16, alignItems: 'center',
  },
  secondaryButtonText: { color: '#8E8E93', fontSize: 16 },
});
```

- [ ] **Step 2: 커밋**

```bash
git add src/screens/CameraScreen.tsx
git commit -m "feat: add CameraScreen with analyze/recipe state machine"
```

---

## Task 8: HistoryScreen 구현

**Files:**
- Create: `src/screens/HistoryScreen.tsx`

- [ ] **Step 1: HistoryScreen.tsx 작성**

`src/screens/HistoryScreen.tsx`:
```tsx
import React, { useState, useCallback, useEffect } from 'react';
import {
  View, Text, StyleSheet, ScrollView, RefreshControl,
} from 'react-native';
import { fetchIngredients, fetchRecipes } from '../api/client';
import { Ingredient, Recipe } from '../types';
import IngredientTag from '../components/IngredientTag';
import RecipeCard from '../components/RecipeCard';

export default function HistoryScreen() {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const [ings, recs] = await Promise.all([fetchIngredients(), fetchRecipes()]);
      setIngredients(ings);
      setRecipes(recs);
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={load} tintColor="#A8E063" />
      }
    >
      <Text style={styles.sectionTitle}>식재료 기록</Text>
      {ingredients.length === 0 ? (
        <Text style={styles.empty}>기록이 없습니다</Text>
      ) : (
        <View style={styles.tagContainer}>
          {ingredients.map(i => (
            <IngredientTag key={i.id ?? i.name} ingredient={i} />
          ))}
        </View>
      )}

      <Text style={[styles.sectionTitle, styles.sectionGap]}>레시피 기록</Text>
      {recipes.length === 0 ? (
        <Text style={styles.empty}>기록이 없습니다</Text>
      ) : (
        recipes.map(r => <RecipeCard key={r.id ?? r.title} recipe={r} />)
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F0F0F' },
  content: { padding: 16, paddingBottom: 32 },
  sectionTitle: { color: '#FFFFFF', fontSize: 18, fontWeight: '700', marginBottom: 12 },
  sectionGap: { marginTop: 24 },
  tagContainer: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 8 },
  empty: { color: '#8E8E93', fontSize: 14, marginBottom: 8 },
});
```

- [ ] **Step 2: 커밋**

```bash
git add src/screens/HistoryScreen.tsx
git commit -m "feat: add HistoryScreen with pull-to-refresh"
```

---

## Task 9: App.tsx — 탭 내비게이션 설정

**Files:**
- Modify: `App.tsx`

- [ ] **Step 1: App.tsx 전체 교체**

`App.tsx`:
```tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import CameraScreen from './src/screens/CameraScreen';
import HistoryScreen from './src/screens/HistoryScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <Tab.Navigator
        screenOptions={{
          tabBarStyle: {
            backgroundColor: '#1C1C1E',
            borderTopColor: '#2C2C2E',
            paddingBottom: 4,
          },
          tabBarActiveTintColor: '#A8E063',
          tabBarInactiveTintColor: '#8E8E93',
          headerStyle: { backgroundColor: '#0F0F0F' },
          headerTintColor: '#FFFFFF',
          headerTitleStyle: { fontWeight: '700' },
        }}
      >
        <Tab.Screen
          name="스캔"
          component={CameraScreen}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="camera" size={size} color={color} />
            ),
            headerTitle: '식재료 스캔',
          }}
        />
        <Tab.Screen
          name="히스토리"
          component={HistoryScreen}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Ionicons name="time" size={size} color={color} />
            ),
            headerTitle: '기록',
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
```

- [ ] **Step 2: Metro 캐시 클리어 후 실행**

```bash
npx expo start --clear
```

Expected: QR 코드 출력, 에러 없음

- [ ] **Step 3: Expo Go 앱으로 QR 스캔 및 탭 바 동작 확인**

확인 항목:
- 다크 배경 화면 렌더링
- 하단에 "스캔" / "히스토리" 탭 표시
- 탭 전환 시 화면 전환
- 활성 탭 아이콘이 `#A8E063` (라임 그린)으로 표시

- [ ] **Step 4: 커밋**

```bash
git add App.tsx
git commit -m "feat: add bottom tab navigation with dark theme"
```

---

## Task 10: E2E 수동 테스트

**Files:** 없음 (테스트 전용 태스크)

> **사전 조건:** FastAPI 서버가 `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`로 실행 중이어야 함. `--host 0.0.0.0` 옵션이 있어야 같은 네트워크의 기기에서 접근 가능.

- [ ] **Step 1: Mac IP 확인 및 .env 업데이트**

```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

출력 예: `inet 192.168.1.42 netmask 0xffffff00 ...`

`.env` 수정:
```
API_URL=http://192.168.1.42:8000
```

Metro 재시작:
```bash
npx expo start --clear
```

- [ ] **Step 2: FastAPI 서버 외부 접근 가능하게 실행**

Food_Camera 디렉토리에서:
```bash
cd /Users/jung/Desktop/Develop/Food_Camera
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected: `INFO: Uvicorn running on http://0.0.0.0:8000`

- [ ] **Step 3: 스캔 탭 — 사진 촬영 흐름 테스트**

1. 스캔 탭 진입 → 📷 아이콘과 "냉장고를 촬영해보세요" 텍스트 확인
2. "사진 찍기 / 선택" 버튼 탭 → ActionSheet 표시 확인
3. 갤러리에서 사과 사진 선택
4. "컴퓨터 비전으로 분석 중..." → "딥러닝 기반 식재료 분석 중..." 메시지 순환 확인
5. 식재료 태그(예: `Apple 91%`) 표시 확인
6. "레시피 추천받기" 버튼 탭
7. "AI가 레시피를 생성 중..." → "맞춤 레시피를 준비 중..." 메시지 순환 확인
8. 레시피 카드(제목 + 내용) 표시 확인
9. "다시 찍기" 버튼으로 초기 화면 복귀 확인

- [ ] **Step 4: 히스토리 탭 — 기록 조회 테스트**

1. 히스토리 탭 이동 → 식재료/레시피 기록 로딩 확인
2. Step 3에서 분석한 식재료와 레시피가 목록에 표시되는지 확인
3. 화면 당겨서 새로고침 → `#A8E063` 색 RefreshControl 표시 확인

- [ ] **Step 5: 에러 케이스 테스트**

`.env`에 잘못된 IP 입력 후 재시작:
```
API_URL=http://1.2.3.4:8000
```
→ "서버에 연결할 수 없습니다" Alert 표시 확인
→ idle 상태로 복귀 확인

올바른 IP로 원복 후 재시작.

- [ ] **Step 6: 최종 커밋**

```bash
git add .
git commit -m "feat: complete Phase 4 React Native app"
```
