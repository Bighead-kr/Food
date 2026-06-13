from pydantic import BaseModel, field_validator
from typing import Optional


class DetectedIngredient(BaseModel):
    name: str
    confidence: float


class AnalyzeResponse(BaseModel):
    ingredients: list[DetectedIngredient]


class RecipeRequest(BaseModel):
    ingredients: list[str]

    @field_validator("ingredients")
    @classmethod
    def ingredients_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("ingredients must not be empty")
        return v


class RecipeResponse(BaseModel):
    title: str
    content: str


class IngredientRecord(BaseModel):
    id: Optional[str] = None
    name: str
    confidence: float
    detected_at: Optional[str] = None


class RecipeRecord(BaseModel):
    id: Optional[str] = None
    ingredients: list[str]
    title: str
    content: str
    created_at: Optional[str] = None
