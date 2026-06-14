from fastapi import FastAPI, UploadFile, File
from model_loader import get_model
import cv2
import numpy as np
import io

app = FastAPI()
model = get_model()

@app.post("/detect")
async def detect_ingredients(file: UploadFile = File(...)):
    # 1. 이미지 읽기
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 2. 모델 추론
    results = model.predict(img)
    
    # 3. 인식된 클래스 이름 추출
    names = model.names
    detected_items = [names[int(box.cls)] for box in results[0].boxes]
    
    # 중복 제거
    unique_items = list(set(detected_items))
    
    return {"detected_items": unique_items}

# 서버 실행 명령: uvicorn main:app --reload