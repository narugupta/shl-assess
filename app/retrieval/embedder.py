"""
Embedding Generator

Generates dense vector embeddings for AssessmentDocument.search_text.

Uses SentenceTransformers.
"""

from __future__ import annotations

import numpy as np
from typing import List

from sentence_transformers import SentenceTransformer

from app.retrieval.schema import AssessmentDocument


class EmbeddingGenerator:

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):

        self.model_name = model_name

        self.model = SentenceTransformer(model_name)

    # -----------------------------------------------------

    def encode_documents(
        self,
        documents: List[AssessmentDocument],
        batch_size: int = 32,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for all assessment documents.
        """

        texts = [doc.search_text for doc in documents]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=True
        )

        return embeddings.astype(np.float32)

    # -----------------------------------------------------

    def encode_query(
        self,
        query: str,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embedding for a user query.
        """

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )

        return embedding.astype(np.float32)

    # -----------------------------------------------------

    def embedding_dimension(self) -> int:
        """
        Returns embedding size.
        """

        return self.model.get_embedding_dimension()

    # -----------------------------------------------------

    def save_embeddings(
        self,
        embeddings: np.ndarray,
        output_file: str
    ) -> None:

        np.save(output_file, embeddings)

    # -----------------------------------------------------

    def load_embeddings(
        self,
        input_file: str
    ) -> np.ndarray:

        return np.load(input_file)