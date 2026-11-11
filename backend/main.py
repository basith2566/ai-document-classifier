"""FastAPI entry point.  Run locally with:  uvicorn main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from routes import documents, stats
from services.classification_service import classifier
from utils.config import settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    classifier.load()
    yield


app = FastAPI(title="AI Document Classification API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "model_ready": classifier.is_ready}


@app.get("/", include_in_schema=False)
def root():
    return {"name": app.title, "docs": "/docs", "health": "/api/health"}
