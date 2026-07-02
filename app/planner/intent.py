"""
Intent Detection Module

This module determines the user's high-level intent.

It DOES NOT:
- extract slots
- retrieve assessments
- make recommendations

It ONLY classifies the user's latest message.
"""

from enum import Enum
import re


class Intent(Enum):
    """
    Supported conversation intents.
    """

    RECOMMEND = "recommend"
    COMPARE = "compare"
    REFINE = "refine"
    JOB_DESCRIPTION = "job_description"
    GREETING = "greeting"
    HELP = "help"
    OFF_TOPIC = "off_topic"
    UNKNOWN = "unknown"


class IntentDetector:
    """
    Rule-based intent detector.

    Fast, deterministic and easily testable.
    """

    def __init__(self):

        self.compare_patterns = [

            r"\bcompare\b",

            r"\bdifference\b",

            r"\bvs\b",

            r"\bversus\b",

            r"\bbetter than\b"

        ]

        self.refine_patterns = [

            r"\bactually\b",

            r"\binstead\b",

            r"\balso\b",

            r"\badd\b",

            r"\bremove\b",

            r"\bonly\b",

            r"\bexclude\b",

            r"\binclude\b"

        ]

        self.jd_patterns = [

            r"job description",

            r"\bjd\b",

            r"responsibilities",

            r"requirements",

            r"qualification",

            r"we are hiring"

        ]

        self.greeting_patterns = [

            r"\bhi\b",

            r"\bhello\b",

            r"\bhey\b",

            r"\bgood morning\b",

            r"\bgood afternoon\b",

            r"\bgood evening\b"

        ]

        self.help_patterns = [

            r"\bhelp\b",

            r"\bhow does this work\b",

            r"\bwhat can you do\b"

        ]

        self.off_topic_patterns = [

            r"weather",

            r"ipl",

            r"football",

            r"movie",

            r"recipe",

            r"python code",

            r"joke",

            r"who won",

            r"capital of"

        ]

    def _match(self, patterns, text):

        """
        Returns True if any regex matches.
        """

        for pattern in patterns:

            if re.search(pattern, text, re.IGNORECASE):

                return True

        return False

    def detect(self, message: str) -> Intent:
        """
        Detect intent from a single user message.
        """

        if not message:
            return Intent.UNKNOWN

        message = message.strip()

        if self._match(self.compare_patterns, message):
            return Intent.COMPARE

        if self._match(self.refine_patterns, message):
            return Intent.REFINE

        if self._match(self.jd_patterns, message):
            return Intent.JOB_DESCRIPTION

        if self._match(self.greeting_patterns, message):
            return Intent.GREETING

        if self._match(self.help_patterns, message):
            return Intent.HELP

        if self._match(self.off_topic_patterns, message):
            return Intent.OFF_TOPIC

        # Default intent
        return Intent.RECOMMEND


# Singleton detector
_detector = IntentDetector()


def detect_intent(message: str) -> Intent:
    """
    Convenience function.

    Example:
        intent = detect_intent(user_message)
    """

    return _detector.detect(message)