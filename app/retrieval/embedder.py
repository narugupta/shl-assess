"""
Embedding Generator

Generates dense vector embeddings for AssessmentDocument.search_text.

Uses fastembed (ONNX Runtime) instead of sentence-transformers/PyTorch.
The ONNX backend uses ~120 MB RAM vs ~500 MB for PyTorch, which is
required to stay within Render's 512 MB free-tier limit.
"""

from __future__ import annotations

import numpy as np
from typing import List

from fastembed import TextEmbedding

from app.retrieval.schema import AssessmentDocument

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_EMBEDDING_DIM = 384


class EmbeddingGenerator:

    def __init__(
        self,
        model_name: str = _MODEL_NAME,
    ):
        self.model_name = model_name
        # fastembed downloads the model on first instantiation and
        # caches it under FASTEMBED_CACHE_PATH (set in Dockerfile to
        # /app/.cache/fastembed so it survives the non-root user switch).
        self.model = TextEmbedding(model_name=model_name)

    # -----------------------------------------------------

    def encode_documents(
        self,
        documents: List[AssessmentDocument],
        **_kwargs,
    ) -> np.ndarray:
        """
        Generate embeddings for all assessment documents.
        fastembed.embed() returns a generator of (384,) float32 arrays
        that are already L2-normalised.
        """
        texts = [doc.search_text for doc in documents]
        embeddings = np.array(list(self.model.embed(texts)), dtype=np.float32)
        return embeddings

    # -----------------------------------------------------

    def encode_query(
        self,
        query: str,
        **_kwargs,
    ) -> np.ndarray:
        """
        Generate embedding for a single user query.
        """
        return np.array(
            list(self.model.embed([query])), dtype=np.float32
        )[0]

    # -----------------------------------------------------

    def embedding_dimension(self) -> int:
        return _EMBEDDING_DIM

    # -----------------------------------------------------

    def save_embeddings(
        self,
        embeddings: np.ndarray,
        output_file: str,
    ) -> None:
        np.save(output_file, embeddings)

    # -----------------------------------------------------

    def load_embeddings(
        self,
        input_file: str,
    ) -> np.ndarray:
        return np.load(input_file)