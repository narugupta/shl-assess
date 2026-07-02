"""
Retrieval Data Models

Defines the data structures used throughout the retrieval
pipeline.

All retrieval modules exchange AssessmentDocument objects
instead of raw dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# Assessment Document
# ============================================================

@dataclass
class AssessmentDocument:
    """
    Canonical representation of one SHL assessment.
    """

    entity_id: str

    name: str

    description: str

    url: str

    duration: Optional[int]

    languages: List[str]

    job_levels: List[str]

    categories: List[str]

    remote: bool

    adaptive: bool

    # Generated during preprocessing
    search_text: str = ""

    metadata: Dict = field(default_factory=dict)


# ============================================================
# Retrieval Query
# ============================================================

@dataclass
class RetrievalQuery:
    """
    Structured query produced by the planner.
    """

    # -------------------------------------------------------
    # Structured slots
    # -------------------------------------------------------

    role: Optional[str] = None

    seniority: Optional[str] = None

    language: Optional[str] = None

    duration: Optional[int] = None

    duration_operator: Optional[str] = None

    hiring_purpose: Optional[str] = None

    # -------------------------------------------------------
    # Lists
    # -------------------------------------------------------

    skills: List[str] = field(default_factory=list)

    categories: List[str] = field(default_factory=list)

    assessment_types: List[str] = field(default_factory=list)

    job_levels: List[str] = field(default_factory=list)

    # -------------------------------------------------------
    # Optional filters
    # -------------------------------------------------------

    remote_required: Optional[bool] = None

    adaptive_required: Optional[bool] = None

    # -------------------------------------------------------
    # Original user query
    # -------------------------------------------------------

    free_text: str = ""

    # -------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"RetrievalQuery("
            f"role={self.role!r}, "
            f"seniority={self.seniority!r}, "
            f"language={self.language!r}, "
            f"duration={self.duration!r})"
        )


# ============================================================
# Retrieval Candidate
# ============================================================

@dataclass
class RetrievalCandidate:
    """
    Candidate returned from BM25, FAISS or Hybrid Retrieval.
    """

    document: AssessmentDocument

    score: float

    source: str

    metadata: Dict = field(default_factory=dict)


# ============================================================
# Retrieval Result
# ============================================================

@dataclass
class RetrievalResult:
    """
    Final output returned by the Retriever.
    """

    query: RetrievalQuery

    candidates: List[RetrievalCandidate]

    elapsed_ms: Optional[float] = None


# ============================================================
# Debug Helpers
# ============================================================

def document_summary(doc: AssessmentDocument) -> Dict:
    """
    Compact representation for debugging.
    """

    return {

        "entity_id": doc.entity_id,

        "name": doc.name,

        "duration": doc.duration,

        "languages": doc.languages,

        "job_levels": doc.job_levels,

        "categories": doc.categories,

        "remote": doc.remote,

        "adaptive": doc.adaptive,

    }


def candidate_summary(candidate: RetrievalCandidate) -> Dict:
    """
    Compact candidate representation.
    """

    return {

        "name": candidate.document.name,

        "score": round(candidate.score, 4),

        "source": candidate.source,

        "metadata": candidate.metadata,

    }