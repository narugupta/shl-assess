"""
BM25 Index

Provides keyword-based retrieval using the BM25 ranking algorithm.

Works alongside FAISS to build a hybrid retrieval system.
"""

from __future__ import annotations

import re
from typing import List

from rank_bm25 import BM25Okapi

from app.retrieval.schema import (
    AssessmentDocument,
    RetrievalCandidate,
)


class BM25Index:

    def __init__(self):

        self.documents: List[AssessmentDocument] = []

        self.corpus_tokens: List[List[str]] = []

        self.index: BM25Okapi | None = None

    # -----------------------------------------------------

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Basic tokenizer.
        """

        text = text.lower()

        return re.findall(r"[a-z0-9.+#]+", text)

    # -----------------------------------------------------

    def build(
        self,
        documents: List[AssessmentDocument]
    ) -> None:
        """
        Build BM25 index.
        """

        self.documents = documents

        self.corpus_tokens = [

            self.tokenize(doc.search_text)

            for doc in documents

        ]

        self.index = BM25Okapi(

            self.corpus_tokens

        )

    # -----------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[RetrievalCandidate]:

        if self.index is None:

            raise RuntimeError(

                "BM25 index has not been built."

            )

        query_tokens = self.tokenize(query)

        scores = self.index.get_scores(query_tokens)

        ranked = sorted(

            enumerate(scores),

            key=lambda x: x[1],

            reverse=True

        )[:top_k]

        results = []

        for idx, score in ranked:

            if score <= 0:

                continue

            results.append(

                RetrievalCandidate(

                    document=self.documents[idx],

                    score=float(score),

                    source="bm25"

                )

            )

        return results

    # -----------------------------------------------------

    def __len__(self):

        return len(self.documents)