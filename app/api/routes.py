"""
API Routes

Defines the HTTP endpoints for the SHL Assessment
Recommendation API.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import get_container
from app.api.models import (
    RecommendRequest,
    RecommendResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ErrorResponse,
)
from app.api.pipeline import RecommendationPipeline

router = APIRouter()

pipeline = RecommendationPipeline()


# ============================================================
# Root
# ============================================================

@router.get(
    "/",
    tags=["General"],
)
async def root():

    return {

        "name": "SHL Assessment Recommendation API",

        "version": "1.0.0",

        "status": "running",

    }


# ============================================================
# Health
# ============================================================

@router.get(

    "/health",

    response_model=HealthResponse,

    tags=["General"],

)

async def health():
    """
    Health endpoint required by the evaluator.
    """

    return HealthResponse(

        status="ok"

    )


# ============================================================
# Frontend Endpoint
# ============================================================

@router.post(

    "/recommend",

    response_model=RecommendResponse,

    responses={

        500: {

            "model": ErrorResponse

        }

    },

    tags=["Frontend"],

)

async def recommend(

    request: RecommendRequest,

):

    try:

        return pipeline.recommend(

            request

        )

    except Exception as exc:

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=str(exc),

        )


# ============================================================
# SHL Evaluator Endpoint
# ============================================================

@router.post(

    "/chat",

    response_model=ChatResponse,

    responses={

        500: {

            "model": ErrorResponse

        }

    },

    tags=["SHL"],

)

async def chat(

    request: ChatRequest,

):

    try:

        return pipeline.chat(

            request

        )

    except Exception as exc:

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=str(exc),

        )


# ============================================================
# Ping
# ============================================================

@router.get(

    "/ping",

    tags=["General"],

)

async def ping():

    return {

        "message": "pong"

    }