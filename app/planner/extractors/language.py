"""
Language Slot Extractor

Extracts supported assessment languages from user messages.

Languages are loaded dynamically from the processed
knowledge base instead of being hardcoded.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class LanguageSlot:
    """
    Represents an extracted language.
    """

    value: Optional[str]

    matched_text: Optional[str] = None

    confidence: float = 1.0

    def __bool__(self):
        return self.value is not None


class LanguageExtractor:
    """
    Extract assessment language from free text.
    """

    def __init__(self, knowledge_base_path: Optional[str] = None):

        self.languages = self._load_languages(
            knowledge_base_path
        )

    def _load_languages(
        self,
        knowledge_base_path: Optional[str],
    ) -> List[str]:
        """
        Load all languages from knowledge_base.json.

        Falls back to a small default list if the file
        cannot be loaded.
        """

        if knowledge_base_path is None:

            root = Path(__file__).resolve().parents[3]

            knowledge_base_path = (
                root
                / "data"
                / "processed"
                / "knowledge_base.json"
            )

        try:

            with open(
                knowledge_base_path,
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)

            languages = set()

            for assessment in data:

                for language in assessment.get(
                    "languages",
                    [],
                ):

                    if language.strip():

                        languages.add(language.strip())

            return sorted(languages)

        except Exception:

            # Safe fallback
            return [

                "English (USA)",

                "English International",

                "Spanish",

                "French",

                "German",

                "Japanese",

                "Italian",

                "Dutch",

            ]

    def extract(
        self,
        text: str,
    ) -> Optional[LanguageSlot]:

        if not text:

            return None

        lower = text.lower()

        # Longest names first
        for language in sorted(
            self.languages,
            key=len,
            reverse=True,
        ):

            pattern = (
                r"\b"
                + re.escape(language.lower())
                + r"\b"
            )

            if re.search(pattern, lower):

                return LanguageSlot(

                    value=language,

                    matched_text=language,

                    confidence=1.0,

                )

        return None

    def extract_language(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Convenience wrapper.
        """

        slot = self.extract(text)

        if slot:

            return slot.value

        return None