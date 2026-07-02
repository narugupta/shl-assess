"""
Category Slot Extractor

Extracts assessment categories from natural language.

Examples
--------
"Need a personality assessment"

"Looking for coding tests"

"I want aptitude tests"

"Need simulations"

The extractor returns standardized SHL categories.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List


@dataclass
class CategorySlot:
    """
    Represents an extracted assessment category.
    """

    value: Optional[str]

    matched_text: Optional[str] = None

    confidence: float = 1.0

    def __bool__(self):
        return self.value is not None


class CategoryExtractor:

    def __init__(self, knowledge_base_path: Optional[str] = None):

        self.categories = self._load_categories(
            knowledge_base_path
        )

        # Natural language aliases
        self.aliases = {

            # Knowledge tests
            "knowledge": "Knowledge & Skills",
            "technical": "Knowledge & Skills",
            "coding": "Knowledge & Skills",
            "programming": "Knowledge & Skills",
            "skill": "Knowledge & Skills",
            "skills": "Knowledge & Skills",

            # Personality
            "personality": "Personality & Behavior",
            "behavior": "Personality & Behavior",
            "behaviour": "Personality & Behavior",
            "behavioral": "Personality & Behavior",
            "behavioural": "Personality & Behavior",

            # Ability
            "ability": "Ability & Aptitude",
            "aptitude": "Ability & Aptitude",
            "cognitive": "Ability & Aptitude",
            "reasoning": "Ability & Aptitude",

            # Simulation
            "simulation": "Simulations",
            "simulations": "Simulations",
            "simulation test": "Simulations",
            "role play": "Simulations",
            "case study": "Simulations",

            # Competency
            "competency": "Competencies",
            "competencies": "Competencies",

            # Development
            "development": "Development & 360",
            "360": "Development & 360",
            "feedback": "Development & 360",

            # Biodata
            "situational": "Biodata & Situational Judgment",
            "judgement": "Biodata & Situational Judgment",
            "judgment": "Biodata & Situational Judgment",
            "sjt": "Biodata & Situational Judgment",

            # Exercises
            "exercise": "Assessment Exercises",
            "assessment exercise": "Assessment Exercises"
        }

    def _load_categories(
        self,
        knowledge_base_path: Optional[str]
    ) -> List[str]:

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
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            categories = set()

            for assessment in data:

                for category in assessment.get(
                    "keys",
                    []
                ):

                    if category.strip():

                        categories.add(category.strip())

            return sorted(categories)

        except Exception:

            return [

                "Knowledge & Skills",

                "Personality & Behavior",

                "Ability & Aptitude",

                "Simulations",

                "Competencies",

                "Development & 360",

                "Assessment Exercises",

                "Biodata & Situational Judgment"

            ]

    def extract(
        self,
        text: str
    ) -> Optional[CategorySlot]:

        if not text:

            return None

        lower = text.lower()

        # ---------- Exact category match ----------

        for category in sorted(
            self.categories,
            key=len,
            reverse=True
        ):

            pattern = (
                r"\b"
                + re.escape(category.lower())
                + r"\b"
            )

            if re.search(pattern, lower):

                return CategorySlot(

                    value=category,

                    matched_text=category,

                    confidence=1.0

                )

        # ---------- Alias matching ----------

        for alias, category in self.aliases.items():

            pattern = (
                r"\b"
                + re.escape(alias)
                + r"\b"
            )

            if re.search(pattern, lower):

                return CategorySlot(

                    value=category,

                    matched_text=alias,

                    confidence=0.95

                )

        return None

    def extract_category(
        self,
        text: str
    ) -> Optional[str]:

        slot = self.extract(text)

        if slot:

            return slot.value

        return None