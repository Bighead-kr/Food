"""
v2 모델 로드 및 클래스 확인 스크립트
실행: python check_model.py
"""
from ultralytics import YOLO
import torch

model = YOLO("weights/best.pt")

print(f"✅ 모델 로드 성공")
print(f"   파라미터: {sum(p.numel() for p in model.model.parameters()):,}")
print(f"   클래스 수: {len(model.names)}")
print(f"   클래스 목록:")
for idx, name in model.names.items():
    print(f"     [{idx}] {name}")

if torch.backends.mps.is_available():
    print("\n✅ MPS(Apple Silicon) 사용 가능 → 추론 가속됩니다")
else:
    print("\n⚠️  MPS 없음 → CPU로 실행됩니다")
