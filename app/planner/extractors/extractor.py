"""
Master Slot Extractor

Coordinates all individual extractors and produces a
single dictionary of extracted slots.

This module contains NO extraction logic.
Each extractor is responsible only for its own slot.
"""

from __future__ import annotations

from typing import Dict, Any

from app.planner.extractors.duration import DurationExtractor
from app.planner.extractors.language import LanguageExtractor
from app.planner.extractors.seniority import SeniorityExtractor
from app.planner.extractors.category import CategoryExtractor
from app.planner.extractors.role import RoleExtractor
from app.planner.extractors.comparison import ComparisonExtractor


class SlotExtractor:
    """
    Runs all slot extractors.

    Example
    -------
    Input:
        "Need a Spanish Java Developer assessment
         under 20 minutes"

    Output:
        {
            "role": ...,
            "language": ...,
            "duration": ...,
            "category": ...,
            "seniority": ...
        }
    """

    def __init__(self):

        self.role_extractor = RoleExtractor()

        self.language_extractor = LanguageExtractor()

        self.seniority_extractor = SeniorityExtractor()

        self.duration_extractor = DurationExtractor()

        self.category_extractor = CategoryExtractor()

        self.comparison_extractor = ComparisonExtractor()

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract every supported slot.

        Returns a dictionary of Slot objects.
        """

        return {

            "role":
                self.role_extractor.extract(text),

            "language":
                self.language_extractor.extract(text),

            "seniority":
                self.seniority_extractor.extract(text),

            "duration":
                self.duration_extractor.extract(text),

            "category":
                self.category_extractor.extract(text)

        }

    def extract_values(self, text: str) -> Dict[str, Any]:
        """
        Convenience wrapper.

        Returns plain values instead of Slot objects.

        Useful for ConversationStateBuilder.
        """

        slots = self.extract(text)

        return {

            "role":
                slots["role"].value
                if slots["role"] else None,

            "language":
                slots["language"].value
                if slots["language"] else None,

            "seniority":
                slots["seniority"].value
                if slots["seniority"] else None,

            "duration":
                slots["duration"].value
                if slots["duration"] else None,

            "duration_operator":
                slots["duration"].operator
                if slots["duration"] else None,

            "category":
                slots["category"].value
                if slots["category"] else None,

            "comparison_items":
                self.comparison_extractor.extract(text)

        }

    def extract_debug(self, text: str) -> Dict[str, Any]:
        """
        Returns everything including confidence scores.

        Useful while developing.
        """

        slots = self.extract(text)

        debug = {}

        for name, slot in slots.items():

            if slot is None:

                debug[name] = None

                continue

            debug[name] = {

                "value": slot.value,

                "confidence": getattr(
                    slot,
                    "confidence",
                    None,
                ),

                "matched_text": getattr(
                    slot,
                    "matched_text",
                    None,
                )

            }

            # Duration has an operator
            if hasattr(slot, "operator"):

                debug[name]["operator"] = slot.operator

        return debug