import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analyze, recipe, data
from app.services.yolo import load_model

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = os.environ.get("MODEL_PATH", "weights/best.pt")
    app.state.model = load_model(model_path)
    print(f"[startup] YOLO model loaded from {model_path}")
    yield
    print("[shutdown] server stopped")


app = FastAPI(title="Food Camera API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(recipe.router)
app.include_router(data.router)
