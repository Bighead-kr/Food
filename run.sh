#!/bin/bash
# Food Camera 백엔드 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# .env 확인
if [ ! -f .env ]; then
  echo "❌ .env 파일이 없습니다. .env.example을 참고해 만들어주세요."
  exit 1
fi

# 가상환경 또는 직접 실행
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

echo "🚀 Food Camera API 시작 중..."
echo "   모델: $(grep MODEL_PATH .env | cut -d= -f2)"
echo "   주소: http://0.0.0.0:8000"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
