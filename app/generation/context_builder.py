"""
Context Builder

Builds grounded context for the LLM from retrieved assessments.

The generated context contains ONLY information from the
knowledge base to minimize hallucinations.
"""

from __future__ import annotations

from typing import List

from app.generation.response import Recommendation


class ContextBuilder:
    """
    Converts recommendations into LLM context.
    """

    def __init__(self):

        self.max_description_length = 500

    # -----------------------------------------------------

    def build(
        self,
        recommendations: List[Recommendation]
    ) -> str:
        """
        Build context for the LLM.
        """

        if not recommendations:

            return "No assessments were retrieved."

        sections = []

        for recommendation in recommendations:

            sections.append(
            
                self._build_document(
                
                    recommendation
        
                )
        
            )

        return "\n\n".join(sections)

    # -----------------------------------------------------

    def _build_document(
        self,
        recommendation: Recommendation,
    ) -> str:
        """
        Convert one retrieved assessment into grounded context.
        """

        doc = recommendation.document

        lines = [

            f"Assessment: {doc.name}",

            f"Reason: {recommendation.reason}",

            f"Confidence: {recommendation.confidence:.2f}",

            f"Description: {self._truncate(doc.description)}",

            f"Duration: {self._duration(doc.duration)}",

            f"Languages: {self._join(doc.languages)}",

            f"Job Levels: {self._join(doc.job_levels)}",

            f"Categories: {self._join(doc.categories)}",

            f"Remote: {'Yes' if doc.remote else 'No'}",

            f"Adaptive: {'Yes' if doc.adaptive else 'No'}",

            f"URL: {doc.url}",

        ]

        return "\n".join(lines)

    # -----------------------------------------------------

    def _truncate(
        self,
        text: str
    ) -> str:

        if not text:

            return "N/A"

        text = text.strip()

        if len(text) <= self.max_description_length:

            return text

        return text[: self.max_description_length] + "..."

    # -----------------------------------------------------

    @staticmethod
    def _join(values):

        if not values:

            return "N/A"

        return ", ".join(values)

    # -----------------------------------------------------

    @staticmethod
    def _duration(value):

        if value is None:

            return "N/A"

        return f"{value} minutes"

    # -----------------------------------------------------

    def build_system_prompt(
        self,
        context: str
    ) -> str:
        """
        Build the grounded system prompt.
        """

        return f"""
You are an SHL assessment recommendation assistant.

You MUST answer ONLY using the information contained below.

If the information is not present,
say you do not know.

Never invent assessment names.

Never invent durations.

Never invent languages.

Never invent URLs.

==============================
KNOWLEDGE BASE
==============================

{context}
"""

    # -----------------------------------------------------

    def build_user_prompt(
        self,
        query: str
    ) -> str:
        """
        Build the user prompt.
        """

        return f"""
User Request

{query}

Provide the best recommendation based ONLY on the knowledge base.
"""