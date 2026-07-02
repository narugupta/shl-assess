"""
Recommendation Pipeline

Coordinates the complete recommendation workflow.

Pipeline
--------
User Query
    │
    ▼
Planner
    │
    ▼
Retriever
    │
    ▼
Context Builder
    │
    ▼
Groq LLM
    │
    ▼
Verifier
    │
    ▼
Formatter
    │
    ▼
API Response
"""

from __future__ import annotations

from typing import Dict, List

from app.api.dependencies import (
    get_planner,
    get_retriever,
    get_context_builder,
    get_generator,
    get_verifier,
    get_formatter,
)

from app.api.models import (
    RecommendRequest,
    RecommendResponse,
    AssessmentRecommendation,
    ChatRequest,
    ChatResponse,
    ChatRecommendation,
)

from app.generation.response import Recommendation

from app.planner.decision import PlannerAction

from app.retrieval.reasoner import RecommendationReasoner

from app.retrieval.schema import RetrievalQuery


class RecommendationPipeline:

    def __init__(self):

        self.planner = get_planner()

        self.retriever = get_retriever()

        self.context_builder = get_context_builder()

        self.generator = get_generator()

        self.verifier = get_verifier()

        self.formatter = get_formatter()

        self.reasoner = RecommendationReasoner()

    # ---------------------------------------------------------
    # Message builders
    # ---------------------------------------------------------

    @staticmethod
    def _build_messages(request: RecommendRequest) -> List[Dict]:
        """
        Builds a role-tagged message list for the /recommend
        (demo frontend) endpoint.

        NOTE: RecommendRequest.conversation_history is a flat list
        of the user's own previous utterances (frontend contract),
        so it is safe to tag every entry as role="user" here.
        This is NOT used for the /chat endpoint - see
        `_messages_from_chat_request` below, which preserves the
        real assistant/user roles from a full transcript.
        """

        messages = []

        for message in request.conversation_history:

            messages.append(
                {
                    "role": "user",
                    "content": message,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": request.query,
            }
        )

        return messages

    @staticmethod
    def _messages_from_chat_request(request: ChatRequest) -> List[Dict]:
        """
        Builds a role-tagged message list straight from the /chat
        transcript, preserving which turns were actually said by
        the user vs. the assistant.

        This fixes a bug where the previous implementation kept
        only the single most recent user message and relabeled
        the assistant's own prior replies as "user" messages,
        silently dropping every earlier user turn (e.g. the
        original job description) before the planner ever saw it.
        """

        return [
            {"role": message.role, "content": message.content}
            for message in request.messages
        ]

    @staticmethod
    def _latest_user_message(messages: List[Dict]) -> str:

        for message in reversed(messages):

            if message.get("role") == "user":

                return message.get("content", "")

        return ""

    @staticmethod
    def _accumulated_user_text(messages: List[Dict]) -> str:
        """
        Concatenates every user turn in order, instead of just the
        latest one.

        Using only the latest message as the retrieval/generation
        query meant a refinement turn like "also add a personality
        assessment" completely replaced the prior shortlist instead
        of extending it (the original "Java developer" context was
        gone from `free_text`, even though role/skills/categories
        persist as structured slots - free text carries real signal
        too, especially for the semantic/BM25 blend and for the
        LLM's own grounding). Verified: before this fix, a
        refinement turn returned only personality-type assessments
        with zero overlap with the original Java-developer shortlist.
        """

        return " ".join(
            message.get("content", "")
            for message in messages
            if message.get("role") == "user"
        ).strip()

    # ---------------------------------------------------------

    @staticmethod
    def _test_type(categories: list[str]) -> str:
        """
        Convert SHL categories into evaluator test types.
        """

        text = " ".join(categories).lower()

        if "knowledge" in text:
            return "K"

        if "ability" in text:
            return "A"

        if "personality" in text:
            return "P"

        if "simulation" in text:
            return "S"

        if "competenc" in text:
            return "C"

        return "O"

    # ---------------------------------------------------------
    # Core pipeline, shared by /recommend and /chat
    # ---------------------------------------------------------

    def _run(
        self,
        messages: List[Dict],
        query: str,
        top_k: int,
        force_recommendation: bool = False,
    ) -> RecommendResponse:
        """
        Execute the full recommendation pipeline over a role-tagged
        message list.

        When force_recommendation is True (turn-cap reached) the
        clarification and non-retrieval branches are bypassed so
        the agent always returns a shortlist on the final allowed
        turn instead of asking another question.
        """

        # -------------------------------------------------
        # Planner
        # -------------------------------------------------

        planner_result = self.planner.plan(messages)

        state = planner_result.state

        # -------------------------------------------------
        # Clarification always wins — UNLESS we are at the
        # turn cap, in which case we must return a shortlist.
        # -------------------------------------------------

        if state.needs_clarification and not force_recommendation:

            return RecommendResponse(
                success=True,
                message=state.clarification_question,
                recommendations=[],
                citations=[],
                verified=True,
            )

        # -------------------------------------------------
        # Non-retrieval planner actions
        #
        # Previously the planner's decision (COMPARE, GREETING,
        # SHOW_HELP, REJECT, UNKNOWN) was computed and then
        # silently discarded, so every message - including
        # off-topic ones that slipped past the guard's keyword
        # list, greetings, and comparison questions - fell
        # through to the generic retrieval + recommend path.
        # -------------------------------------------------

        # Non-retrieval actions are bypassed at turn cap so the
        # agent always attempts retrieval on the last turn.
        if not force_recommendation:

            if planner_result.action == PlannerAction.REJECT:

                return RecommendResponse(
                    success=True,
                    message=planner_result.message
                    or "I can only help with SHL assessment recommendations.",
                    recommendations=[],
                    citations=[],
                    verified=True,
                )

            if planner_result.action == PlannerAction.GREETING:

                return RecommendResponse(
                    success=True,
                    message=planner_result.message
                    or "Hello! How can I help you find the right SHL assessment today?",
                    recommendations=[],
                    citations=[],
                    verified=True,
                )

            if planner_result.action == PlannerAction.SHOW_HELP:

                return RecommendResponse(
                    success=True,
                    message=planner_result.message
                    or "I can recommend, compare, and refine SHL assessments for a role.",
                    recommendations=[],
                    citations=[],
                    verified=True,
                )

            if planner_result.action == PlannerAction.UNKNOWN:

                return RecommendResponse(
                    success=True,
                    message=planner_result.message
                    or "I'm not sure how to help with that. Could you rephrase?",
                    recommendations=[],
                    citations=[],
                    verified=True,
                )

        # -------------------------------------------------
        # Retrieval Query (shared by RETRIEVE and COMPARE)
        # -------------------------------------------------

        retrieval_query = RetrievalQuery(
            role=state.role,
            seniority=state.seniority,
            language=state.language,
            duration=state.duration,
            duration_operator=state.duration_operator,
            skills=state.skills,
            categories=state.categories,
            assessment_types=state.assessment_types,
            free_text=query,
        )

        # -------------------------------------------------
        # Retrieve
        # -------------------------------------------------

        retrieval = self.retriever.retrieve(
            retrieval_query,
            top_k=top_k,
        )

        recommendations = []

        for rank, candidate in enumerate(retrieval.candidates, start=1):

            recommendations.append(
                Recommendation(
                    document=candidate.document,
                    rank=rank,
                    confidence=candidate.score,
                    reason=self.reasoner.build(
                        candidate.document,
                        retrieval_query,
                    ),
                )
            )

        # -------------------------------------------------
        # Context
        # -------------------------------------------------

        context = self.context_builder.build(recommendations)

        # -------------------------------------------------
        # LLM
        #
        # COMPARE uses the dedicated comparison prompt so a
        # question like "what's the difference between OPQ and
        # GSA" is answered as a grounded comparison instead of
        # being pushed through the generic recommend prompt.
        # A comparison is informational, not a committed
        # shortlist, so we don't emit `recommendations` for it.
        # -------------------------------------------------

        if planner_result.action == PlannerAction.COMPARE:

            generation = self.generator.compare(
                query=query,
                context=context,
            )

            generation.recommendations = []
            generation.citations = [
                recommendation.document.url
                for recommendation in recommendations
            ]

        else:

            generation = self.generator.recommend(
                query=query,
                context=context,
            )

            generation.recommendations = recommendations
            generation.citations = [
                recommendation.document.url
                for recommendation in recommendations
            ]

        # -------------------------------------------------
        # Verification
        # -------------------------------------------------

        verification = self.verifier.verify(generation)

        generation.warnings.extend(verification.issues)

        # -------------------------------------------------
        # Formatting
        # -------------------------------------------------

        final = self.formatter.format(generation)

        # -------------------------------------------------
        # API Response
        # -------------------------------------------------

        api_recommendations = []

        for recommendation in final.recommendations:

            document = recommendation.document

            api_recommendations.append(
                AssessmentRecommendation(
                    rank=recommendation.rank,
                    name=document.name,
                    url=document.url,
                    duration=document.duration,
                    languages=document.languages,
                    job_levels=document.job_levels,
                    categories=document.categories,
                    confidence=recommendation.confidence,
                    reason=recommendation.reason,
                )
            )

        return RecommendResponse(
            success=True,
            message=final.message,
            recommendations=api_recommendations,
            citations=final.citations,
            verified=final.verified,
        )

    # ---------------------------------------------------------
    # /recommend (demo frontend)
    # ---------------------------------------------------------

    def recommend(
        self,
        request: RecommendRequest,
    ) -> RecommendResponse:
        """
        Execute the full recommendation pipeline for the demo
        frontend endpoint.
        """

        messages = self._build_messages(request)

        return self._run(
            messages=messages,
            query=request.query,
            top_k=request.top_k,
        )

    # ---------------------------------------------------------
    # /chat (SHL evaluator)
    # ---------------------------------------------------------

    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Compatibility wrapper for the SHL evaluator.
        """

        if not request.messages:

            return ChatResponse(
                reply="Please provide a hiring requirement.",
                recommendations=[],
                end_of_conversation=False,
            )

        messages = self._messages_from_chat_request(request)

        query_text = self._accumulated_user_text(messages)

        # The evaluator caps conversations at 8 turns total (user +
        # assistant combined). The messages list here is the history
        # BEFORE our reply, so len(messages)==7 means our reply will
        # be turn 8 — the last allowed one. At that point we must
        # emit a committed shortlist and close the conversation;
        # asking another clarifying question would push past the cap.
        at_turn_cap = len(messages) >= 7

        response = self._run(
            messages=messages,
            query=query_text,
            top_k=10,
            force_recommendation=at_turn_cap,
        )

        recommendations = []

        for recommendation in response.recommendations:

            recommendations.append(
                ChatRecommendation(
                    name=recommendation.name,
                    url=recommendation.url,
                    test_type=self._test_type(
                        recommendation.categories
                    ),
                )
            )

        is_done = at_turn_cap or self._is_conversation_done(
            messages, response
        )

        return ChatResponse(
            reply=response.message,
            recommendations=recommendations,
            end_of_conversation=is_done,
        )

    # ---------------------------------------------------------
    # end_of_conversation heuristic
    # ---------------------------------------------------------

    def _is_conversation_done(
        self,
        messages: List[Dict],
        response: RecommendResponse,
    ) -> bool:
        """
        Decides whether the conversation is actually finished.

        The gold traces make it clear that giving a shortlist does
        NOT mean the conversation is over: every provided trace has
        `end_of_conversation: false` on every turn except the very
        last one, even on turns that already contain a shortlist -
        the shortlist evolves across turns as the user refines it.

        A stateless service has no memory of what it said before, so
        this rebuilds state from the transcript with and without the
        latest user turn and checks whether that turn actually added
        anything new. Only close the conversation once:
          - a shortlist already existed before this turn (so the
            user has had at least one chance to refine it), AND
          - this turn didn't change any extracted slot (role,
            seniority, language, duration, skills, categories,
            comparison items) - i.e. it reads like a confirmation/
            no-op rather than a real refinement.
        The hard 8-turn cap is also enforced here as a safety net.
        """

        if not response.recommendations:
            return False

        # Handled before this method is called when at_turn_cap is
        # True, but guard here too in case of direct calls.
        if len(messages) >= 7:
            return True

        prior_messages = messages[:-1]

        if not prior_messages:
            # This is the very first shortlist - give the user a
            # chance to refine before closing.
            return False

        prior_state = self.planner.plan(prior_messages).state

        if prior_state.needs_clarification:
            # This is the first turn where we actually had enough to
            # recommend - don't close immediately.
            return False

        current_state = self.planner.plan(messages).state

        changed = (
            prior_state.role != current_state.role
            or prior_state.seniority != current_state.seniority
            or prior_state.language != current_state.language
            or prior_state.duration != current_state.duration
            or set(prior_state.categories) != set(current_state.categories)
            or set(prior_state.skills) != set(current_state.skills)
            or set(prior_state.comparison_items)
            != set(current_state.comparison_items)
        )

        return not changed
