"""
Conversation History Builder

Since the API is stateless, every request contains the
entire conversation history.

This module rebuilds ConversationState from all previous
messages.
"""

from __future__ import annotations

from typing import Dict, List

from app.planner.intent import detect_intent
from app.planner.state import ConversationState
from app.planner.extractors.extractor import SlotExtractor


class ConversationHistoryBuilder:
    """
    Builds ConversationState from message history.
    """

    def __init__(self):

        self.extractor = SlotExtractor()

    def build(
        self,
        messages: List[Dict]
    ) -> ConversationState:

        state = ConversationState()

        if not messages:
            return state

        user_turn_count = 0
        last_user_text = ""

        for message in messages:

            role = message.get("role", "")

            if role != "user":
                continue

            text = message.get("content", "").strip()

            if not text:
                continue

            user_turn_count += 1
            last_user_text = text

            state.add_history(text)

            slots = self.extractor.extract_values(text)

            # -----------------------------
            # Intent
            # -----------------------------

            state.intent = detect_intent(text)

            # -----------------------------
            # Role
            # -----------------------------

            if slots["role"]:

                state.role = slots["role"]

            # -----------------------------
            # Seniority
            # -----------------------------

            if slots["seniority"]:

                state.seniority = slots["seniority"]

            # -----------------------------
            # Language
            # -----------------------------

            if slots["language"]:

                state.language = slots["language"]

            # -----------------------------
            # Duration
            # -----------------------------

            if slots["duration"]:

                state.duration = slots["duration"]

                state.duration_operator = slots[
                    "duration_operator"
                ]

            # -----------------------------
            # Category
            # -----------------------------

            if slots["category"]:

                state.add_category(
                    slots["category"]
                )

            # -----------------------------
            # Comparison Items
            # -----------------------------

            for item in slots.get("comparison_items") or []:

                state.add_comparison_item(item)

            # -----------------------------
            # Save extracted slots
            # -----------------------------

            state.extracted_slots.update(

                {

                    k: v

                    for k, v in slots.items()

                    if v is not None

                }

            )

        # -----------------------------
        # Role fallback
        #
        # The role extractor only recognizes a fixed vocabulary of
        # job-title words. If the user has already answered at
        # least once (this is at least their 2nd turn) and no role
        # was ever extracted, asking "what role are you hiring for?"
        # again would just repeat forever, right up to the 8-turn
        # cap, without ever producing a shortlist. Fall back to the
        # user's own words as a best-effort role signal instead -
        # it still feeds retrieval as free text/ranking signal
        # (see Retriever._build_query_text, Ranker), it's just not
        # a strict filter, so an imperfect fallback is safe here.
        # -----------------------------

        if not state.role and user_turn_count >= 2 and last_user_text:

            state.role = last_user_text[:120]

        return state

    def latest_user_message(
        self,
        messages: List[Dict]
    ) -> str:

        """
        Returns latest user message.
        """

        for message in reversed(messages):

            if message.get("role") == "user":

                return message.get("content", "")

        return ""

    def user_messages(
        self,
        messages: List[Dict]
    ) -> List[str]:

        """
        Returns all user messages.
        """

        return [

            m["content"]

            for m in messages

            if m.get("role") == "user"

        ]