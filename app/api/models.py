"""
API Models

Pydantic models for the FastAPI interface.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ============================================================
# SHL Chat API Models
# ============================================================

class ChatMessage(BaseModel):
    """
    One conversation message.
    """

    role: Literal["user", "assistant"] = Field(
        ...,
        description="Message role.",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="Message text.",
    )


class ChatRequest(BaseModel):
    """
    Request body for POST /chat.
    """

    messages: List[ChatMessage] = Field(
        ...,
        min_length=1,
        description="Complete conversation history.",
    )


class ChatRecommendation(BaseModel):
    """
    Recommendation returned by the SHL evaluator endpoint.
    """

    name: str

    url: str

    test_type: str


class ChatResponse(BaseModel):
    """
    Response returned by POST /chat.
    """

    reply: str

    recommendations: List[ChatRecommendation] = Field(
        default_factory=list
    )

    end_of_conversation: bool


# ============================================================
# Frontend Request Model
# ============================================================

class RecommendRequest(BaseModel):
    """
    Request body for /recommend.
    Used by the demo frontend.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="User hiring requirement.",
    )

    conversation_history: List[str] = Field(
        default_factory=list,
        description="Previous conversation turns.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of recommendations.",
    )


# ============================================================
# Frontend Recommendation
# ============================================================

class AssessmentRecommendation(BaseModel):
    """
    Rich recommendation shown by the demo UI.
    """

    rank: int

    name: str

    url: str

    duration: Optional[int] = None

    languages: List[str] = Field(default_factory=list)

    job_levels: List[str] = Field(default_factory=list)

    categories: List[str] = Field(default_factory=list)

    confidence: float

    reason: str


# ============================================================
# Frontend Response
# ============================================================

class RecommendResponse(BaseModel):
    """
    Response returned by /recommend.
    """

    success: bool = True

    message: str

    recommendations: List[
        AssessmentRecommendation
    ] = Field(default_factory=list)

    citations: List[str] = Field(
        default_factory=list
    )

    verified: bool = True


# ============================================================
# Health
# ============================================================

class HealthResponse(BaseModel):
    """
    Health endpoint response.
    """

    status: str = "ok"

    version: Optional[str] = None

    planner_ready: Optional[bool] = None

    retriever_ready: Optional[bool] = None

    generator_ready: Optional[bool] = None


# ============================================================
# Error
# ============================================================

class ErrorResponse(BaseModel):
    """
    Generic error response.
    """

    success: bool = False

    error: str

    details: Optional[str] = None