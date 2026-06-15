from fastapi import APIRouter, HTTPException
from app.models.schemas import DetectedIngredient
from app.services.supabase_client import get_client, get_ingredients, get_recipes, delete_ingredient, save_ingredients, clear_all_ingredients, clear_all_recipes

router = APIRouter()


@router.get("/ingredients")
async def list_ingredients():
    db = get_client()
    return get_ingredients(db)


@router.post("/ingredients", status_code=201)
async def add_ingredients(body: dict):
    ingredients_data = body.get("ingredients", [])
    if not ingredients_data:
        raise HTTPException(status_code=400, detail="ingredients required")
    try:
        items = [DetectedIngredient(**i) for i in ingredients_data]
        db = get_client()
        save_ingredients(db, items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ingredients/{ingredient_id}")
async def remove_ingredient(ingredient_id: str):
    try:
        db = get_client()
        delete_ingredient(db, ingredient_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recipes")
async def list_recipes():
    db = get_client()
    return get_recipes(db)


@router.delete("/ingredients")
async def clear_ingredients():
    db = get_client()
    clear_all_ingredients(db)


@router.delete("/recipes")
async def clear_recipes():
    db = get_client()
    clear_all_recipes(db)
