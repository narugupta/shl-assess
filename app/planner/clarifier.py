"""
Clarification Engine

Determines whether the assistant has enough information
to perform retrieval.

It does NOT retrieve assessments.

It only decides:

1. Is clarification needed?
2. Which slot is missing?
3. What question should be asked?
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.planner.state import ConversationState
from app.planner.intent import Intent


@dataclass
class ClarificationResult:

    needs_clarification: bool

    missing_slot: Optional[str] = None

    question: Optional[str] = None


class Clarifier:

    """
    Rule-based clarification engine.
    """

    def __init__(self):

        self.questions = {

            "role":
                "What role are you hiring for?",

            "seniority":
                "What experience level is this role intended for?",

            "language":
                "Which language should the assessment support?",

            "duration":
                "Do you have a preferred assessment duration?",

            "category":
                "Are you looking for a technical, personality, aptitude or simulation assessment?"

        }

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def evaluate(
        self,
        state: ConversationState
    ) -> ClarificationResult:

        """
        Decide whether clarification is required.
        """

        # Greeting

        if state.intent == Intent.GREETING:

            return ClarificationResult(False)

        # Help

        if state.intent == Intent.HELP:

            return ClarificationResult(False)

        # Off-topic

        if state.intent == Intent.OFF_TOPIC:

            return ClarificationResult(False)

        # Comparison

        if state.intent == Intent.COMPARE:

            if len(state.comparison_items) < 2:

                return ClarificationResult(

                    True,

                    "comparison",

                    "Which two assessments would you like me to compare?"

                )

            return ClarificationResult(False)

        # Job description

        if state.intent == Intent.JOB_DESCRIPTION:

            return ClarificationResult(False)

        # Recommendation

        return self._recommendation_rules(state)

    # ---------------------------------------------------------
    # Recommendation Rules
    # ---------------------------------------------------------

    def _recommendation_rules(

        self,

        state: ConversationState

    ) -> ClarificationResult:

        """
        Rules for recommendation requests.
        """

        # Role is mandatory

        if not state.role:

            return self._ask("role")

        # Seniority is optional for now.
        # Many SHL assessments support multiple levels.

        # Language is optional.
        # Default to English.

        # Duration is optional.

        return ClarificationResult(False)

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _ask(

        self,

        slot: str

    ) -> ClarificationResult:

        return ClarificationResult(

            needs_clarification=True,

            missing_slot=slot,

            question=self.questions.get(slot)

        )

    def update_state(

        self,

        state: ConversationState

    ) -> ConversationState:

        """
        Update ConversationState with clarification info.
        """

        result = self.evaluate(state)

        state.needs_clarification = (

            result.needs_clarification

        )

        state.clarification_question = (

            result.question

        )

        if result.missing_slot:

            state.missing_slots = [

                result.missing_slot

            ]

        else:

            state.missing_slots = []

        return state