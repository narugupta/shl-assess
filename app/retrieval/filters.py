"""
Retrieval Filters

Filters retrieval candidates using structured constraints
produced by the conversation planner.
"""

from __future__ import annotations

from typing import List

from app.retrieval.schema import (
    RetrievalCandidate,
    RetrievalQuery,
)


class CandidateFilter:

    """
    Applies structured filters to retrieval candidates.
    """

    def filter(
        self,
        candidates: List[RetrievalCandidate],
        query: RetrievalQuery,
    ) -> List[RetrievalCandidate]:

        filtered = candidates

        filtered = self._filter_language(
            filtered,
            query
        )

        filtered = self._filter_seniority(
            filtered,
            query
        )

        filtered = self._filter_category(
            filtered,
            query
        )

        filtered = self._filter_duration(
            filtered,
            query
        )

        return filtered

    # --------------------------------------------------------

    def _filter_language(
        self,
        candidates,
        query
    ):

        if not query.language:

            return candidates

        result = []

        target = query.language.lower()

        for candidate in candidates:

            languages = [

                lang.lower()

                for lang in candidate.document.languages

            ]

            if target in languages:

                result.append(candidate)

        return result

    # --------------------------------------------------------

    def _filter_seniority(
        self,
        candidates,
        query
    ):

        if not query.seniority:

            return candidates

        result = []

        target = query.seniority.lower()

        for candidate in candidates:

            levels = [

                level.lower()

                for level in candidate.document.job_levels

            ]

            if target in levels:

                result.append(candidate)

        return result

    # --------------------------------------------------------

    def _filter_category(
        self,
        candidates,
        query
    ):
        """
        Deliberately NOT a hard filter.

        `query.categories` accumulates additively across the whole
        conversation (see ConversationState.add_category / the
        planner's history builder) - it represents "also include
        this type" (e.g. "actually, add a personality assessment"),
        not "only show this type". A hard AND-filter here meant that
        once ANY category was ever mentioned, every candidate from
        every other category was discarded outright - so a
        refinement turn didn't extend the previous shortlist, it
        replaced it entirely and lost everything that was correctly
        relevant a turn earlier (verified: a "Java developer" ->
        "also add a personality assessment" conversation went from
        an all-Java shortlist to an all-personality shortlist with
        zero overlap).

        CandidateRanker.rerank() already applies category overlap as
        a soft ranking bonus, so category preference is still
        respected - it just no longer eliminates otherwise-relevant
        candidates. Unlike category, language/seniority/duration are
        left as hard filters since those genuinely are exclusionary
        constraints ("must be in French") rather than additive ones.
        """

        return candidates

    # --------------------------------------------------------

    def _filter_duration(
        self,
        candidates,
        query
    ):

        if query.duration is None:

            return candidates

        result = []

        for candidate in candidates:

            duration = candidate.document.duration

            if duration is None:

                continue

            op = query.duration_operator

            if op == "lte":

                if duration <= query.duration:

                    result.append(candidate)

            elif op == "gte":

                if duration >= query.duration:

                    result.append(candidate)

            else:

                if duration == query.duration:

                    result.append(candidate)

        return result

    # --------------------------------------------------------

    def filter_remote(
        self,
        candidates,
        remote_required: bool,
    ):

        return [

            c

            for c in candidates

            if c.document.remote == remote_required

        ]

    # --------------------------------------------------------

    def filter_adaptive(
        self,
        candidates,
        adaptive_required: bool,
    ):

        return [

            c

            for c in candidates

            if c.document.adaptive == adaptive_required

        ]