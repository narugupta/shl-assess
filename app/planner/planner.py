"""
Conversation Planner

This is the main orchestration layer for Phase 2.

Pipeline
--------
messages
    │
    ▼
Guard Engine
    │
    ▼
Conversation History Builder
    │
    ▼
ConversationState
    │
    ▼
Clarifier
    │
    ▼
Decision Engine
    │
    ▼
PlannerResult

No retrieval happens here.
Phase 3 will consume PlannerResult.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.planner.history import ConversationHistoryBuilder
from app.planner.clarifier import Clarifier
from app.planner.decision import (
    DecisionEngine,
    PlannerAction,
)
from app.planner.state import ConversationState
from app.planner.guards import GuardEngine, GuardStatus


@dataclass
class PlannerResult:
    """
    Output returned by the planner.
    """

    action: PlannerAction
    state: ConversationState
    message: Optional[str] = None


class Planner:
    """
    Main planning pipeline.

    Responsibilities:
    1. Run safety guards.
    2. Build conversation state.
    3. Clarify missing information.
    4. Decide the next action.
    """

    def __init__(self):
        self.history_builder = ConversationHistoryBuilder()
        self.clarifier = Clarifier()
        self.decision_engine = DecisionEngine()
        self.guard = GuardEngine()

    def plan(
        self,
        messages: List[Dict],
    ) -> PlannerResult:
        """
        Execute the planning pipeline.
        """

        # -------------------------------------------------
        # Find latest user message
        # -------------------------------------------------

        latest_message = ""

        for message in reversed(messages):
            if message.get("role") == "user":
                latest_message = message.get("content", "")
                break

        # -------------------------------------------------
        # Safety / Guard checks
        # -------------------------------------------------

        guard_result = self.guard.check(latest_message)

        if guard_result.status == GuardStatus.BLOCK:
            return PlannerResult(
                action=PlannerAction.REJECT,
                state=ConversationState(),
                message=guard_result.message,
            )

        # -------------------------------------------------
        # Build conversation state
        # -------------------------------------------------

        state = self.history_builder.build(messages)

        # -------------------------------------------------
        # Clarify missing slots
        # -------------------------------------------------

        state = self.clarifier.update_state(state)

        # -------------------------------------------------
        # Decide next action
        # -------------------------------------------------

        decision = self.decision_engine.decide(state)

        return PlannerResult(
            action=decision.action,
            state=state,
            message=decision.message,
        )

    def debug(
        self,
        messages: List[Dict],
    ) -> Dict:
        """
        Return a debugging representation of the planner.
        """

        result = self.plan(messages)

        return {
            "action": result.action.value,
            "message": result.message,
            "state": result.state.summary(),
            "history": result.state.history_summary,
            "slots": result.state.extracted_slots,
        }