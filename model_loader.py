from ultralytics import YOLO
import torch

def get_model():
    # 모델 로드
    model = YOLO('weights/best.pt')
    
    # M4 Mac의 MPS(Metal Performance Shaders) 사용 설정
    if torch.backends.mps.is_available():
        model.to('mps')
        print("✅ M4 Mac MPS 가속 사용 중")
    else:
        print("⚠️ MPS를 사용할 수 없습니다. CPU로 실행합니다.")
        
    return model