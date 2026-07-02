"""
Conversation State

This file contains the central state object used by the
conversation planner.

Every request reconstructs this object from the complete
conversation history because the API is stateless.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

from app.planner.intent import Intent


@dataclass
class ConversationState:
    """
    Represents everything the planner currently knows about
    the user's hiring request.
    """

    # ==========================================================
    # Hiring Information
    # ==========================================================

    role: Optional[str] = None

    seniority: Optional[str] = None

    language: Optional[str] = None

    duration: Optional[int] = None

    duration_operator: Optional[str] = None

    hiring_purpose: Optional[str] = None
    # Examples:
    # recruitment
    # development
    # reskilling

    # ==========================================================
    # Extracted Skills
    # ==========================================================

    skills: List[str] = field(default_factory=list)

    # ==========================================================
    # Assessment Filters
    # ==========================================================

    assessment_types: List[str] = field(default_factory=list)

    categories: List[str] = field(default_factory=list)

    job_levels: List[str] = field(default_factory=list)

    remote_required: Optional[bool] = None

    adaptive_required: Optional[bool] = None

    # ==========================================================
    # Planner Information
    # ==========================================================

    intent: Intent = Intent.UNKNOWN

    needs_clarification: bool = False

    clarification_question: Optional[str] = None

    missing_slots: List[str] = field(default_factory=list)

    # ==========================================================
    # Comparison Mode
    # ==========================================================

    comparison_items: List[str] = field(default_factory=list)

    # ==========================================================
    # Refinement Mode
    # ==========================================================

    refinement: bool = False

    # ==========================================================
    # Debug Information
    # ==========================================================

    extracted_slots: Dict[str, Any] = field(default_factory=dict)

    history_summary: List[str] = field(default_factory=list)

    # ==========================================================
    # Utility Methods
    # ==========================================================

    def reset_clarification(self):
        """
        Clears clarification status.
        """

        self.needs_clarification = False
        self.clarification_question = None
        self.missing_slots = []

    def add_skill(self, skill: str):
        """
        Adds a skill only if not already present.
        """

        if not skill:
            return

        if skill not in self.skills:
            self.skills.append(skill)

    def add_category(self, category: str):
        """
        Adds category without duplication.
        """

        if not category:
            return

        if category not in self.categories:
            self.categories.append(category)

    def add_comparison_item(self, item: str):
        """
        Adds a referenced assessment name for COMPARE mode,
        without duplication.
        """

        if not item:
            return

        if item not in self.comparison_items:
            self.comparison_items.append(item)

    def add_job_level(self, level: str):
        """
        Adds job level without duplication.
        """

        if not level:
            return

        if level not in self.job_levels:
            self.job_levels.append(level)

    def add_assessment_type(self, assessment_type: str):
        """
        Adds assessment type without duplication.
        """

        if not assessment_type:
            return

        if assessment_type not in self.assessment_types:
            self.assessment_types.append(assessment_type)

    def add_history(self, text: str):
        """
        Stores processed user messages.
        """

        if text:
            self.history_summary.append(text)

    def to_dict(self):
        """
        Converts state to dictionary.
        Useful for debugging and logging.
        """

        data = asdict(self)

        data["intent"] = self.intent.value

        return data

    def summary(self):
        """
        Compact summary for logging.
        """

        return {

            "role": self.role,

            "seniority": self.seniority,

            "language": self.language,

            "duration": self.duration,

            "skills": self.skills,

            "categories": self.categories,

            "assessment_types": self.assessment_types,

            "intent": self.intent.value,

            "needs_clarification": self.needs_clarification,

            "missing_slots": self.missing_slots

        }

    def __str__(self):
        """
        Pretty printing.
        """

        return str(self.summary())