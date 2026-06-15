FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# CPU-only PyTorch 설치 (ultralytics가 CUDA 버전 당기는 것 방지)
RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# torch/ultralytics/cv2 설치 후 numpy 2.x로 업그레이드될 수 있으므로 강제 다운그레이드
# cv2 바이너리는 numpy 1.x ABI(_signature_descriptor)를 요구함
RUN pip install --no-cache-dir --force-reinstall "numpy==1.26.4"

COPY . .

ENV MODEL_PATH=weights/best.pt

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
