"""
Response Models

Defines the structured objects exchanged between the
generation components.

Pipeline

Retriever
    │
    ▼
GenerationResponse
    │
    ▼
Verifier
    │
    ▼
Formatter
    │
    ▼
Final User Response
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app.retrieval.schema import AssessmentDocument


# ============================================================
# Recommendation
# ============================================================

@dataclass
class Recommendation:
    """
    One recommended assessment.
    """

    document: AssessmentDocument

    reason: str

    confidence: float = 1.0

    rank: int = 1


# ============================================================
# Comparison
# ============================================================

@dataclass
class Comparison:
    """
    Comparison between two assessments.
    """

    left: AssessmentDocument

    right: AssessmentDocument

    summary: str


# ============================================================
# Clarification
# ============================================================

@dataclass
class Clarification:
    """
    Used when additional information is required.
    """

    question: str

    missing_slots: List[str] = field(default_factory=list)


# ============================================================
# Generation Response
# ============================================================

@dataclass
class GenerationResponse:
    """
    Output of the LLM before formatting.
    """

    recommendations: List[Recommendation] = field(default_factory=list)

    comparison: Optional[Comparison] = None

    clarification: Optional[Clarification] = None

    answer: str = ""

    verified: bool = True

    citations: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)


# ============================================================
# Verification Result
# ============================================================

@dataclass
class VerificationResult:
    """
    Result of hallucination verification.
    """

    passed: bool

    issues: List[str] = field(default_factory=list)


# ============================================================
# Final Response
# ============================================================

@dataclass
class FinalResponse:
    """
    Final object returned to the API.
    """

    message: str

    recommendations: List[Recommendation] = field(default_factory=list)

    citations: List[str] = field(default_factory=list)

    verified: bool = True


# ============================================================
# Helper Functions
# ============================================================

def recommendation_summary(
    recommendation: Recommendation,
) -> dict:
    """
    Compact representation for debugging.
    """

    doc = recommendation.document

    return {

        "rank": recommendation.rank,

        "name": doc.name,

        "duration": doc.duration,

        "confidence": round(
            recommendation.confidence,
            3
        ),

        "reason": recommendation.reason

    }


def response_summary(
    response: GenerationResponse,
) -> dict:
    """
    Compact summary.
    """

    return {

        "recommendations": len(
            response.recommendations
        ),

        "comparison": response.comparison is not None,

        "clarification": response.clarification is not None,

        "citations": len(
            response.citations
        ),

        "warnings": response.warnings

    }