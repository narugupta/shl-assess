"""
Duration Slot Extractor

Extracts duration constraints from user messages.

Examples:
    "Need something under 20 minutes"
    "Maximum 30 min assessment"
    "Around 15 minutes"
    "Less than 45 mins"
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class DurationSlot:
    """
    Represents an extracted duration constraint.
    """

    value: Optional[int]
    operator: str = "equal"

    def __bool__(self):
        return self.value is not None


class DurationExtractor:
    """
    Extracts duration information from free text.
    """

    def __init__(self):

        self.patterns = [

            # under 20 minutes
            (
                re.compile(
                    r"(under|less than|below|maximum|max)\s*(\d+)\s*(minute|minutes|min|mins)",
                    re.IGNORECASE,
                ),
                "lte",
            ),

            # at least 30 minutes
            (
                re.compile(
                    r"(over|more than|greater than|minimum|min)\s*(\d+)\s*(minute|minutes|min|mins)",
                    re.IGNORECASE,
                ),
                "gte",
            ),

            # exactly 20 minutes
            (
                re.compile(
                    r"(\d+)\s*(minute|minutes|min|mins)",
                    re.IGNORECASE,
                ),
                "equal",
            ),
        ]

        self.special_cases = {

            "half hour": 30,

            "half an hour": 30,

            "one hour": 60,

            "1 hour": 60,

            "an hour": 60,
        }

    def extract(self, text: str) -> Optional[DurationSlot]:
        """
        Extract duration from text.

        Returns:
            DurationSlot or None
        """

        if not text:
            return None

        text = text.lower().strip()

        # Handle phrases like "half hour"
        for phrase, minutes in self.special_cases.items():

            if phrase in text:

                return DurationSlot(
                    value=minutes,
                    operator="equal",
                )

        # Regex patterns
        for pattern, operator in self.patterns:

            match = pattern.search(text)

            if match:

                value = int(match.group(2)) if operator != "equal" else int(match.group(1))

                return DurationSlot(
                    value=value,
                    operator=operator,
                )

        return None

    def extract_minutes(self, text: str) -> Optional[int]:
        """
        Convenience wrapper.

        Returns only the numeric value.
        """

        slot = self.extract(text)

        if slot:
            return slot.value

        return None