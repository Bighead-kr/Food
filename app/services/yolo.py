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
            if conf < 0.35:
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
