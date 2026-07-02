"""
Knowledge Base Preprocessor

Builds searchable text for each assessment.

The generated search_text is used by:
    - BM25
    - Sentence Transformer embeddings
"""

from __future__ import annotations

import re
from typing import List

from app.retrieval.schema import AssessmentDocument


class KnowledgeBasePreprocessor:

    def preprocess(
        self,
        documents: List[AssessmentDocument]
    ) -> List[AssessmentDocument]:
        """
        Preprocess every assessment.
        """

        processed = []

        for doc in documents:

            doc.search_text = self.build_search_text(doc)

            processed.append(doc)

        return processed

    # -----------------------------------------------------

    def build_search_text(
        self,
        doc: AssessmentDocument
    ) -> str:
        """
        Build one searchable text block.
        """

        parts = []

        # -------------------------------------------------
        # Assessment name (highest importance)
        # -------------------------------------------------

        if doc.name:
            parts.extend([doc.name] * 3)

        # -------------------------------------------------
        # Categories
        # -------------------------------------------------

        if doc.categories:
            parts.extend(doc.categories)

        # -------------------------------------------------
        # Job Levels
        # -------------------------------------------------

        if doc.job_levels:
            parts.extend(doc.job_levels)

        # -------------------------------------------------
        # Languages
        # -------------------------------------------------

        if doc.languages:
            parts.extend(doc.languages)

        # -------------------------------------------------
        # Duration
        # -------------------------------------------------

        if doc.duration is not None:
            parts.append(f"{doc.duration} minutes")

        # -------------------------------------------------
        # Remote
        # -------------------------------------------------

        if doc.remote:
            parts.append("remote")

        # -------------------------------------------------
        # Adaptive
        # -------------------------------------------------

        if doc.adaptive:
            parts.append("adaptive")

        # -------------------------------------------------
        # Description (very important)
        # -------------------------------------------------

        if doc.description:
            parts.append(doc.description)

        text = "\n".join(parts)

        return self.clean_text(text)

    # -----------------------------------------------------

    def clean_text(
        self,
        text: str
    ) -> str:
        """
        Normalize whitespace.
        """

        text = text.replace("&", " and ")

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # -----------------------------------------------------

    def preview(
        self,
        document: AssessmentDocument
    ) -> str:
        """
        Pretty preview.
        """

        return document.search_text[:500]