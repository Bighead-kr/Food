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
