import os
from fastapi import APIRouter
from app.models.schemas import RecipeRequest, RecipeResponse
from app.services.gemini import generate_recipe
from app.services.supabase_client import get_client, save_recipe

router = APIRouter()


@router.post("/recipe", response_model=RecipeResponse)
async def create_recipe(body: RecipeRequest):
    api_key = os.environ["GEMINI_API_KEY"]
    title, content = generate_recipe(body.ingredients, api_key=api_key)

    db = get_client()
    save_recipe(db, body.ingredients, title, content)

    return RecipeResponse(title=title, content=content)
