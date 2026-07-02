"""
FAISS Vector Index

Provides semantic similarity search over assessment embeddings.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import faiss
import numpy as np

from app.retrieval.schema import (
    AssessmentDocument,
    RetrievalCandidate,
)


class FAISSIndex:

    def __init__(self):

        self.index = None

        self.documents: List[AssessmentDocument] = []

    # ---------------------------------------------------------

    def build(
        self,
        embeddings: np.ndarray,
        documents: List[AssessmentDocument]
    ) -> None:
        """
        Build a FAISS index from normalized embeddings.
        """

        if len(documents) != embeddings.shape[0]:
            raise ValueError(
                "Number of documents and embeddings do not match."
            )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.documents = documents

    # ---------------------------------------------------------

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> List[RetrievalCandidate]:
        """
        Semantic search using cosine similarity.
        """

        if self.index is None:
            raise RuntimeError(
                "Index has not been built."
            )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(
            query_embedding.astype(np.float32),
            top_k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            results.append(

                RetrievalCandidate(

                    document=self.documents[idx],

                    score=float(score),

                    source="faiss"

                )

            )

        return results

    # ---------------------------------------------------------

    def save(
        self,
        output_file: str
    ) -> None:

        if self.index is None:
            raise RuntimeError(
                "Nothing to save."
            )

        Path(output_file).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            output_file
        )

    # ---------------------------------------------------------

    def load(
        self,
        input_file: str,
        documents: List[AssessmentDocument]
    ) -> None:

        self.index = faiss.read_index(
            input_file
        )

        self.documents = documents

    # ---------------------------------------------------------

    def ntotal(self) -> int:

        if self.index is None:
            return 0

        return self.index.ntotal