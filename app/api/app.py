"""
FastAPI Application

Entry point for the SHL Assessment Recommendation API.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.dependencies import get_container
from app.api.routes import router


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

FRONTEND_DIR = BASE_DIR / "frontend"


# ============================================================
# Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize shared resources once when the application starts.
    """

    print("=" * 60)
    print("Initializing SHL Recommendation System...")
    print("=" * 60)

    get_container()

    print("System Ready.")
    print("=" * 60)

    yield

    print("=" * 60)
    print("Shutting down SHL Recommendation System...")
    print("=" * 60)


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(

    title="SHL Assessment Recommendation API",

    description=(
        "Recommendation API for SHL assessments using "
        "Hybrid Retrieval (BM25 + FAISS) and Groq LLM."
    ),

    version="1.0.0",

    lifespan=lifespan,

    docs_url="/docs",

    redoc_url="/redoc",

)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# ============================================================
# Static Files
# ============================================================

app.mount(

    "/static",

    StaticFiles(directory=FRONTEND_DIR),

    name="static",

)


# ============================================================
# Frontend
# ============================================================

@app.get(
    "/ui",
    include_in_schema=False,
)
async def ui():
    """
    Serves the demo frontend.
    """

    return FileResponse(

        FRONTEND_DIR / "index.html"

    )


# ============================================================
# API Routes
# ============================================================

app.include_router(router)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "app.api.app:app",

        host="0.0.0.0",

        port=8000,

        reload=True,

    )