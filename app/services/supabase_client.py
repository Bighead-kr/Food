import os
from supabase import create_client, Client
from app.models.schemas import DetectedIngredient


def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def save_ingredients(client: Client, ingredients: list[DetectedIngredient]) -> None:
    rows = [{"name": i.name, "confidence": i.confidence} for i in ingredients]
    client.table("ingredients").insert(rows).execute()


def save_recipe(client: Client, ingredients: list[str], title: str, content: str) -> None:
    client.table("recipes").insert({
        "ingredients": ingredients,
        "title": title,
        "content": content,
    }).execute()


def get_ingredients(client: Client) -> list[dict]:
    result = (
        client.table("ingredients")
        .select("*")
        .order("detected_at", desc=True)
        .limit(20)
        .execute()
    )
    return result.data


def get_recipes(client: Client) -> list[dict]:
    result = (
        client.table("recipes")
        .select("*")
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    return result.data
