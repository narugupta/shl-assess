"""
Retriever

Main retrieval pipeline.

Pipeline
--------
Knowledge Base
      │
      ▼
Loader
      │
      ▼
Preprocessor
      │
      ▼
Embeddings
      │
      ▼
FAISS + BM25
      │
      ▼
Hybrid Retrieval
      │
      ▼
Filtering
      │
      ▼
Re-ranking
      │
      ▼
Top Results
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from app.retrieval.loader import KnowledgeBaseLoader
from app.retrieval.preprocess import KnowledgeBasePreprocessor
from app.retrieval.embedder import EmbeddingGenerator
from app.retrieval.faiss_index import FAISSIndex
from app.retrieval.bm25_index import BM25Index
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.filters import CandidateFilter
from app.retrieval.ranker import CandidateRanker

from app.retrieval.schema import (
    RetrievalQuery,
    RetrievalResult,
)

logger = logging.getLogger(__name__)

_EMBEDDINGS_CACHE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "embeddings.npy"
)


class Retriever:

    def __init__(self):

        # ----------------------------
        # Load Knowledge Base
        # ----------------------------

        loader = KnowledgeBaseLoader()

        self.documents = loader.load()

        # ----------------------------
        # Preprocess
        # ----------------------------

        processor = KnowledgeBasePreprocessor()

        self.documents = processor.preprocess(
            self.documents
        )

        # ----------------------------
        # Embeddings  (load cache or recompute)
        # ----------------------------

        self.embedder = EmbeddingGenerator()

        embeddings = self._load_or_build_embeddings(self.documents)

        # ----------------------------
        # FAISS
        # ----------------------------

        self.faiss = FAISSIndex()

        self.faiss.build(
            embeddings,
            self.documents
        )

        # ----------------------------
        # BM25
        # ----------------------------

        self.bm25 = BM25Index()

        self.bm25.build(
            self.documents
        )

        # ----------------------------
        # Hybrid
        # ----------------------------

        self.hybrid = HybridRetriever(

            bm25=self.bm25,

            faiss=self.faiss,

            embedder=self.embedder

        )

        # ----------------------------
        # Filter
        # ----------------------------

        self.filter = CandidateFilter()

        # ----------------------------
        # Ranker
        # ----------------------------

        self.ranker = CandidateRanker()

    # ----------------------------------------------------

    def _load_or_build_embeddings(self, documents) -> np.ndarray:
        """
        Load cached embeddings from disk when available and still
        valid (same document count). Recompute and persist otherwise.

        Without a cache, every cold start encodes the full catalog
        via sentence-transformers which takes 30-60 s and risks
        breaching the evaluator's 2-minute readiness window.
        """

        if _EMBEDDINGS_CACHE.exists():
            try:
                cached = np.load(_EMBEDDINGS_CACHE).astype(np.float32)
                if cached.shape[0] == len(documents):
                    logger.info(
                        "Loaded %d embeddings from cache (%s).",
                        cached.shape[0],
                        _EMBEDDINGS_CACHE,
                    )
                    return cached
                logger.warning(
                    "Cache has %d rows but knowledge base has %d docs; "
                    "recomputing.",
                    cached.shape[0],
                    len(documents),
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not load embedding cache: %s", exc)

        logger.info("Computing embeddings for %d documents.", len(documents))
        embeddings = self.embedder.encode_documents(documents)
        try:
            _EMBEDDINGS_CACHE.parent.mkdir(parents=True, exist_ok=True)
            np.save(_EMBEDDINGS_CACHE, embeddings)
            logger.info("Saved embedding cache to %s.", _EMBEDDINGS_CACHE)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not write embedding cache: %s", exc)
        return embeddings

    # ----------------------------------------------------

    def retrieve(

        self,

        query: RetrievalQuery,

        top_k: int = 10

    ) -> RetrievalResult:

        """
        Complete retrieval pipeline.
        """

        # ------------------------
        # Build search query
        # ------------------------

        search_query = self._build_query_text(query)

        # ------------------------
        # Hybrid Retrieval
        # ------------------------

        candidates = self.hybrid.search(

            search_query,

            top_k=max(top_k * 3, 30)

        )

        # ------------------------
        # Structured Filtering
        # ------------------------

        candidates = self.filter.filter(

            candidates,

            query

        )

        # ------------------------
        # Re-ranking
        # ------------------------

        candidates = self.ranker.rerank(

            candidates,

            query

        )

        # ------------------------
        # Top K
        # ------------------------

        candidates = self.ranker.top_k(

            candidates,

            top_k

        )

        return RetrievalResult(

            query=query,

            candidates=candidates

        )

    # ----------------------------------------------------

    def _build_query_text(

        self,

        query: RetrievalQuery

    ) -> str:

        """
        Convert RetrievalQuery into
        one semantic search string.
        """

        parts = []

        if query.role:

            parts.append(query.role)

        if query.seniority:

            parts.append(query.seniority)

        if query.language:

            parts.append(query.language)

        parts.extend(query.skills)

        parts.extend(query.categories)

        if query.free_text:

            parts.append(query.free_text)

        return " ".join(parts)

    # ----------------------------------------------------

    def search(

        self,

        text: str,

        top_k: int = 10

    ):

        """
        Convenience method.

        Search using plain text.
        """

        query = RetrievalQuery(

            free_text=text,

            role=text

        )

        return self.retrieve(

            query,

            top_k

        )