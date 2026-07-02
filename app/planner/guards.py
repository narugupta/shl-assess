"""
Guard Engine

Runs before the planner.

Responsibilities
----------------

1. Prompt Injection Detection
2. Jailbreak Detection
3. Off-topic Detection
4. Empty Input Detection
5. Oversized Prompt Detection
6. Retrieval Manipulation Detection

Returns GuardResult.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class GuardStatus(Enum):

    PASS = "pass"

    BLOCK = "block"


@dataclass
class GuardResult:

    status: GuardStatus

    reason: str | None = None

    message: str | None = None


class GuardEngine:

    def __init__(self):

        self.max_length = 5000

        # -----------------------------
        # Prompt Injection
        # -----------------------------

        self.prompt_injection = [

            r"ignore (all |any |previous |prior )?(safety |operating )?(rules|instructions|guidelines)",

            r"forget (all |your )?(previous |prior )?instructions",

            r"disregard (all |your |previous |prior )?(safety |operating )?(rules|instructions|guidelines)",

            r"system prompt",

            r"system override",

            r"reveal prompt",

            r"show hidden prompt",

            r"developer message",

            r"internal instructions",

            r"act as chatgpt",

            r"pretend to be",

            r"jailbreak",

            r"do anything now",

            r"\bdan\b",

            r"\bsystem\s*:",

            r"admin credentials"

        ]

        # -----------------------------
        # Retrieval Manipulation
        # -----------------------------

        self.retrieval_patterns = [

            r"show every assessment",

            r"return entire database",

            r"dump database",

            r"list internal ids",

            r"entity_id",

            r"knowledge_base",

            r"json data"

        ]

        # -----------------------------
        # Off Topic
        # -----------------------------

        self.off_topic = [

            r"\bweather\b",

            r"\bipl\b",

            r"\bfootball\b",

            r"\bmovie\b",

            r"\brecipe\b",

            r"capital of",

            r"python tutorial",

            r"leetcode",

            r"linux command",

            # Legal questions - spec explicitly requires refusing
            # these rather than answering or silently falling
            # through to a generic clarification question.
            r"\bis it legal\b",

            r"\blegal(ly)? to (fire|terminate|reject|dismiss|not hire)\b",

            r"\bdiscriminat(e|ion|ory)\b",

            r"\bsue\b",

            r"\blawsuit\b",

            r"\bemployment lawyer\b",

            r"\blabor law\b",

            r"\blabour law\b",

            r"\bminimum wage\b",

            # General hiring advice - spec requires refusing these
            # too; we only want to answer *which assessment*, not
            # broader HR/people-management questions.
            r"\bshould i (fire|hire|promote|lay off)\b",

            r"\bhow (do|should) i interview\b",

            r"\bwhat interview questions\b",

            r"\bhow to negotiate salary\b",

            r"\bwhat salary\b",

            r"\bhow much (should|to) (i )?(pay|offer)\b",

            r"\bsalary (range|band) (for|to offer)\b",

            r"\bwrite (a |an )?job (description|posting|listing)\b",

            r"\bwrite (a |an )?rejection (email|letter)\b",

        ]

    # ------------------------------------------------

    def check(self, text: str) -> GuardResult:

        if text is None:

            return GuardResult(

                GuardStatus.BLOCK,

                "empty",

                "Please enter a message."

            )

        text = text.strip()

        if len(text) == 0:

            return GuardResult(

                GuardStatus.BLOCK,

                "empty",

                "Please enter a message."

            )

        if len(text) > self.max_length:

            return GuardResult(

                GuardStatus.BLOCK,

                "too_long",

                "The message is too long."

            )

        lower = text.lower()

        # -----------------------------
        # Prompt Injection
        # -----------------------------

        for pattern in self.prompt_injection:

            if re.search(pattern, lower):

                return GuardResult(

                    GuardStatus.BLOCK,

                    "prompt_injection",

                    "I can't follow instructions that attempt to override my operating instructions."

                )

        # -----------------------------
        # Retrieval Manipulation
        # -----------------------------

        for pattern in self.retrieval_patterns:

            if re.search(pattern, lower):

                return GuardResult(

                    GuardStatus.BLOCK,

                    "retrieval_attack",

                    "I can't expose internal knowledge-base data."

                )

        # -----------------------------
        # Off Topic
        # -----------------------------

        for pattern in self.off_topic:

            if re.search(pattern, lower):

                return GuardResult(

                    GuardStatus.BLOCK,

                    "off_topic",

                    "I'm designed to help with SHL assessment recommendations."

                )

        return GuardResult(

            GuardStatus.PASS

        )