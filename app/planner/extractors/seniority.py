"""
Seniority Slot Extractor

Extracts standardized SHL job levels from natural language.

Examples:
    "Need a graduate assessment"
    "Hiring a senior backend engineer"
    "Looking for directors"
    "Freshers"
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SenioritySlot:
    """
    Represents an extracted seniority level.
    """

    value: Optional[str]

    matched_text: Optional[str] = None

    confidence: float = 1.0

    def __bool__(self):
        return self.value is not None


class SeniorityExtractor:
    """
    Maps user language to SHL job levels.
    """

    def __init__(self):

        self.patterns = [

            # ---------------------------------------------------
            # Graduate
            # ---------------------------------------------------

            (
                "Graduate",

                [
                    r"\bgraduate\b",
                    r"\bgraduates\b",
                    r"\bcampus hire\b",
                    r"\bcampus hiring\b",
                    r"\bgraduate program\b",
                    r"\bcollege hire\b",
                ],
            ),

            # ---------------------------------------------------
            # Entry-Level
            # ---------------------------------------------------

            (
                "Entry-Level",

                [
                    r"\bentry level\b",
                    r"\bentry-level\b",
                    r"\bfresher\b",
                    r"\bfreshers\b",
                    r"\bjunior\b",
                    r"\bnew hire\b",
                    r"\bnew graduate\b",
                    r"\b0[- ]?1 years?\b",
                ],
            ),

            # ---------------------------------------------------
            # Mid-Professional
            # ---------------------------------------------------

            (
                "Mid-Professional",

                [
                    r"\bmid level\b",
                    r"\bmid-level\b",
                    r"\bmid professional\b",
                    r"\bexperienced\b",
                    r"\b2[- ]?5 years?\b",
                    r"\b3[- ]?5 years?\b",
                    r"\b5 years experience\b",
                ],
            ),

            # ---------------------------------------------------
            # Professional Individual Contributor
            # ---------------------------------------------------

            (
                "Professional Individual Contributor",

                [
                    r"\bsenior engineer\b",
                    r"\bsenior developer\b",
                    r"\bindividual contributor\b",
                    r"\bic role\b",
                    r"\btechnical specialist\b",
                    r"\bsenior software engineer\b",
                    r"\blead engineer\b",
                ],
            ),

            # ---------------------------------------------------
            # Front Line Manager
            # ---------------------------------------------------

            (
                "Front Line Manager",

                [
                    r"\bteam lead\b",
                    r"\blead\b",
                    r"\bfront line manager\b",
                    r"\bline manager\b",
                ],
            ),

            # ---------------------------------------------------
            # Manager
            # ---------------------------------------------------

            (
                "Manager",

                [
                    r"\bmanager\b",
                    r"\bengineering manager\b",
                    r"\bproduct manager\b",
                    r"\bproject manager\b",
                    r"\bhiring manager\b",
                ],
            ),

            # ---------------------------------------------------
            # Director
            # ---------------------------------------------------

            (
                "Director",

                [
                    r"\bdirector\b",
                    r"\bhead of\b",
                    r"\bdepartment head\b",
                ],
            ),

            # ---------------------------------------------------
            # Executive
            # ---------------------------------------------------

            (
                "Executive",

                [
                    r"\bexecutive\b",
                    r"\bvp\b",
                    r"\bvice president\b",
                    r"\bcxo\b",
                    r"\bceo\b",
                    r"\bcto\b",
                    r"\bcfo\b",
                    r"\bcoo\b",
                ],
            ),

            # ---------------------------------------------------
            # General Population
            # ---------------------------------------------------

            (
                "General Population",

                [
                    r"\bgeneral population\b",
                    r"\beveryone\b",
                    r"\ball employees\b",
                ],
            ),

        ]

    def extract(self, text: str) -> Optional[SenioritySlot]:
        """
        Extract standardized SHL seniority.
        """

        if not text:
            return None

        text = text.lower()

        for level, patterns in self.patterns:

            for pattern in patterns:

                match = re.search(pattern, text, re.IGNORECASE)

                if match:

                    return SenioritySlot(

                        value=level,

                        matched_text=match.group(),

                        confidence=1.0,

                    )

        return None

    def extract_level(self, text: str) -> Optional[str]:
        """
        Convenience wrapper.
        """

        slot = self.extract(text)

        if slot:
            return slot.value

        return None