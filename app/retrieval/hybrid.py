"""
Hybrid Retriever

Combines BM25 and FAISS retrieval.

Pipeline

User Query
      │
      ▼
 BM25 Search
      │
      ▼
 FAISS Search
      │
      ▼
 Merge Scores
      │
      ▼
 Return Top Results
"""

from __future__ import annotations

from typing import Dict, List

from app.retrieval.schema import (
    RetrievalCandidate,
)

from app.retrieval.bm25_index import BM25Index
from app.retrieval.faiss_index import FAISSIndex
from app.retrieval.embedder import EmbeddingGenerator


class HybridRetriever:

    def __init__(
        self,
        bm25: BM25Index,
        faiss: FAISSIndex,
        embedder: EmbeddingGenerator,
    ):

        self.bm25 = bm25

        self.faiss = faiss

        self.embedder = embedder

    # ----------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
        bm25_weight: float = 0.5,
        faiss_weight: float = 0.5,
    ) -> List[RetrievalCandidate]:

        bm25_results = self.bm25.search(
            query,
            top_k=top_k * 2
        )

        query_embedding = self.embedder.encode_query(query)

        faiss_results = self.faiss.search(
            query_embedding,
            top_k=top_k * 2
        )

        merged = self._merge_results(
            bm25_results,
            faiss_results,
            bm25_weight,
            faiss_weight,
        )

        merged.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return merged[:top_k]

    # ----------------------------------------------------

    def _merge_results(
        self,
        bm25_results: List[RetrievalCandidate],
        faiss_results: List[RetrievalCandidate],
        bm25_weight: float,
        faiss_weight: float,
    ) -> List[RetrievalCandidate]:

        merged: Dict[str, RetrievalCandidate] = {}

        # ---------------------------
        # Normalize BM25
        # ---------------------------

        bm25_max = max(
            (r.score for r in bm25_results),
            default=1.0
        )

        for result in bm25_results:

            score = result.score / bm25_max

            merged[result.document.entity_id] = RetrievalCandidate(

                document=result.document,

                score=score * bm25_weight,

                source="hybrid",

                metadata={

                    "bm25": result.score,

                    "faiss": 0.0

                }

            )

        # ---------------------------
        # Normalize FAISS
        # ---------------------------

        faiss_max = max(
            (r.score for r in faiss_results),
            default=1.0
        )

        for result in faiss_results:

            score = result.score / faiss_max

            entity = result.document.entity_id

            if entity in merged:

                merged[entity].score += score * faiss_weight

                merged[entity].metadata["faiss"] = result.score

            else:

                merged[entity] = RetrievalCandidate(

                    document=result.document,

                    score=score * faiss_weight,

                    source="hybrid",

                    metadata={

                        "bm25": 0.0,

                        "faiss": result.score

                    }

                )

        return list(merged.values())