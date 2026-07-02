"""
Candidate Ranker

Re-ranks retrieval candidates using structured planner output
and lightweight heuristic scoring.
"""

from __future__ import annotations

import math
from typing import List

from app.retrieval.schema import (
    RetrievalCandidate,
    RetrievalQuery,
)


class CandidateRanker:
    """
    Lightweight heuristic reranker.

    Adds small bonuses based on structured query fields
    extracted by the planner.
    """

    def rerank(
        self,
        candidates: List[RetrievalCandidate],
        query: RetrievalQuery,
    ) -> List[RetrievalCandidate]:

        for candidate in candidates:

            doc = candidate.document

            bonus = 0.0

            # -------------------------------------------------
            # Role / Title Match
            # -------------------------------------------------

            if query.role:

                role = query.role.lower().strip()

                title = doc.name.lower()

                if role == title:

                    bonus += 0.35

                elif role in title:

                    bonus += 0.25

                else:

                    matches = sum(

                        1

                        for word in role.split()

                        if word in title

                    )

                    bonus += 0.05 * matches

            # -------------------------------------------------
            # Skill Match
            # -------------------------------------------------

            if query.skills:

                description = (doc.description or "").lower()

                for skill in query.skills:

                    if skill.lower() in description:

                        bonus += 0.08

            # -------------------------------------------------
            # Language Match
            # -------------------------------------------------

            if query.language:

                languages = {

                    language.lower()

                    for language in doc.languages

                }

                if query.language.lower() in languages:

                    bonus += 0.20

            # -------------------------------------------------
            # Seniority Match
            # -------------------------------------------------

            if query.seniority:

                if query.seniority in doc.job_levels:

                    bonus += 0.20

            # -------------------------------------------------
            # Category Match
            # -------------------------------------------------

            if query.categories:

                overlap = {

                    category.lower()

                    for category in query.categories

                }.intersection(

                    {

                        category.lower()

                        for category in doc.categories

                    }

                )

                bonus += 0.12 * len(overlap)

            # -------------------------------------------------
            # Duration Match
            # -------------------------------------------------

            if (

                query.duration is not None

                and doc.duration is not None

            ):

                if query.duration_operator == "lte":

                    if doc.duration <= query.duration:

                        bonus += 0.15

                elif query.duration_operator == "gte":

                    if doc.duration >= query.duration:

                        bonus += 0.15

                else:

                    diff = abs(

                        doc.duration - query.duration

                    )

                    if diff == 0:

                        bonus += 0.20

                    elif diff <= 5:

                        bonus += 0.10

            # -------------------------------------------------
            # Free-text Overlap
            # -------------------------------------------------

            if query.free_text:

                searchable_text = (

                    f"{doc.name} {doc.description}"

                ).lower()

                for token in query.free_text.lower().split():

                    if len(token) <= 2:

                        continue

                    if token in searchable_text:

                        bonus += 0.01

            # -------------------------------------------------
            # Prevent bonus explosion
            # -------------------------------------------------

            bonus = min(bonus, 0.60)

            raw_score = candidate.score + bonus

            candidate.score = self._sigmoid(raw_score)

            candidate.metadata["rerank_bonus"] = round(

                bonus,

                3,

            )

        candidates.sort(

            key=lambda candidate: candidate.score,

            reverse=True,

        )

        return candidates

    # -------------------------------------------------

    @staticmethod
    def _sigmoid(score: float) -> float:
        """
        Normalize score into [0, 1].
        """

        return 1.0 / (1.0 + math.exp(-score))

    # -------------------------------------------------

    @staticmethod
    def top_k(
        candidates: List[RetrievalCandidate],
        k: int = 10,
    ) -> List[RetrievalCandidate]:

        return candidates[:k]