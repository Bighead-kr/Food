from fastapi import APIRouter
from app.services.supabase_client import get_client, get_ingredients, get_recipes

router = APIRouter()


@router.get("/ingredients")
async def list_ingredients():
    db = get_client()
    return get_ingredients(db)


@router.get("/recipes")
async def list_recipes():
    db = get_client()
    return get_recipes(db)
