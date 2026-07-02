"""
Planner Decision Engine

This module decides the next action after the conversation
state has been reconstructed and clarified.

It NEVER modifies the ConversationState.

Responsibilities
----------------
1. Read ConversationState
2. Decide next action
3. Return PlannerDecision
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.planner.state import ConversationState
from app.planner.intent import Intent


class PlannerAction(Enum):

    ASK_CLARIFICATION = "ask_clarification"

    RETRIEVE = "retrieve"

    COMPARE = "compare"

    SHOW_HELP = "show_help"

    GREETING = "greeting"

    REJECT = "reject"

    UNKNOWN = "unknown"


@dataclass
class PlannerDecision:

    action: PlannerAction

    message: Optional[str] = None


class DecisionEngine:

    """
    Reads ConversationState and decides the next action.
    """

    def decide(
        self,
        state: ConversationState
    ) -> PlannerDecision:

        # -----------------------------
        # Clarification always wins
        # -----------------------------

        if state.needs_clarification:

            return PlannerDecision(

                action=PlannerAction.ASK_CLARIFICATION,

                message=state.clarification_question

            )

        # -----------------------------
        # Greetings
        # -----------------------------

        if state.intent == Intent.GREETING:

            return PlannerDecision(

                PlannerAction.GREETING,

                "Hello! How can I help you find the right SHL assessment today?"

            )

        # -----------------------------
        # Help
        # -----------------------------

        if state.intent == Intent.HELP:

            return PlannerDecision(

                PlannerAction.SHOW_HELP,

                (
                    "I can recommend SHL assessments, compare assessments, "
                    "and help you choose assessments for hiring or development."
                )

            )

        # -----------------------------
        # Off-topic
        # -----------------------------

        if state.intent == Intent.OFF_TOPIC:

            return PlannerDecision(

                PlannerAction.REJECT,

                (
                    "I'm designed to help with SHL assessment recommendations "
                    "and related hiring questions."
                )

            )

        # -----------------------------
        # Comparison
        # -----------------------------

        if state.intent == Intent.COMPARE:

            return PlannerDecision(

                PlannerAction.COMPARE

            )

        # -----------------------------
        # Job Description
        # -----------------------------

        if state.intent == Intent.JOB_DESCRIPTION:

            return PlannerDecision(

                PlannerAction.RETRIEVE

            )

        # -----------------------------
        # Refinement
        # -----------------------------

        if state.intent == Intent.REFINE:

            return PlannerDecision(

                PlannerAction.RETRIEVE

            )

        # -----------------------------
        # Recommendation
        # -----------------------------

        if state.intent == Intent.RECOMMEND:

            return PlannerDecision(

                PlannerAction.RETRIEVE

            )

        # -----------------------------
        # Unknown
        # -----------------------------

        return PlannerDecision(

            PlannerAction.UNKNOWN,

            "I'm not sure how to help with that."

        )