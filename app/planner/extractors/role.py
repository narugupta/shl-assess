"""
Role Slot Extractor

Extracts the target job role from natural language.

Examples
--------
Need Java Developer assessment
-> Java Developer

Hiring Senior Backend Engineer
-> Backend Engineer

Looking for Finance Analyst
-> Finance Analyst

Need Principal Software Architect
-> Software Architect
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class RoleSlot:
    value: Optional[str]
    matched_text: Optional[str] = None
    confidence: float = 1.0

    def __bool__(self):
        return self.value is not None


class RoleExtractor:

    def __init__(self):

        # Words commonly appearing before the role
        self.prefixes = [

            "need",
            "looking for",
            "looking",
            "hire",
            "hiring",
            "require",
            "required",
            "searching for",
            "find",
            "assessment for",
            "assessment of",
            "candidate for"

        ]

        # Seniority modifiers
        self.seniority_words = {

            "senior",
            "sr",
            "sr.",
            "junior",
            "jr",
            "jr.",
            "lead",
            "principal",
            "staff",
            "chief",
            "graduate",
            "mid",
            "mid-level",
            "midlevel",
            "entry",
            "entry-level",
            "experienced",
            "fresher"

        }

        # Words that usually end the role
        self.trailing_words = {

            "assessment",
            "assessments",
            "test",
            "tests",
            "role",
            "roles",
            "position",
            "positions",
            "opening",
            "openings",
            "candidate",
            "candidates"

        }

        self.role_suffixes = [

            "developer",
            "engineer",
            "architect",
            "programmer",

            "analyst",
            "scientist",
            "consultant",
            "administrator",

            "manager",
            "director",
            "executive",
            "officer",

            "designer",
            "tester",
            "specialist",
            "recruiter",

            "accountant",
            "auditor",
            "technician",

            "associate",
            "coordinator",

            "intern",
            "graduate",

            # Broader / non-tech, non-office roles that are just as
            # common in real hiring queries but were missing before
            # (e.g. "admin assistants" previously matched nothing).
            "assistant",
            "assistants",
            "agent",
            "agents",
            "representative",
            "representatives",
            "rep",
            "reps",
            "clerk",
            "clerks",
            "cashier",
            "cashiers",
            "teller",
            "tellers",
            "operator",
            "operators",
            "supervisor",
            "supervisors",
            "driver",
            "drivers",
            "nurse",
            "nurses",
            "teacher",
            "teachers",
            "receptionist",
            "receptionists",
            "worker",
            "workers",
            "leader",
            "leaders",
            "lead",
            "leads",
            "rep.",

        ]

        suffix_pattern = "|".join(
            map(re.escape, self.role_suffixes)
        )

        self.pattern = re.compile(

            rf"""
            (
                (?:[A-Za-z0-9.+#/&-]+\s+){{0,5}}
                (?:{suffix_pattern})
            )
            """,

            re.IGNORECASE | re.VERBOSE

        )

    # --------------------------------------------------

    def _remove_prefixes(self, text: str) -> str:

        text = text.strip()

        changed = True

        while changed:

            changed = False

            lower = text.lower()

            for prefix in sorted(
                self.prefixes,
                key=len,
                reverse=True
            ):

                if lower.startswith(prefix):

                    text = text[len(prefix):].strip()

                    changed = True

                    break

        return text

    # --------------------------------------------------

    def _clean_role(self, role: str) -> str:

        role = role.strip()

        role = re.sub(r"\s+", " ", role)

        words = role.split()

        # Remove seniority words

        while words and words[0].lower() in self.seniority_words:

            words.pop(0)

        # Remove trailing assessment words

        while words and words[-1].lower() in self.trailing_words:

            words.pop()

        role = " ".join(words)

        return role.title()

    # --------------------------------------------------

    def extract(self, text: str) -> Optional[RoleSlot]:

        if not text:

            return None

        text = self._remove_prefixes(text)

        match = self.pattern.search(text)

        if not match:

            return None

        role = self._clean_role(match.group(1))

        if not role:

            return None

        confidence = 0.95

        if len(role.split()) == 1:

            confidence = 0.90

        return RoleSlot(

            value=role,

            matched_text=match.group(0),

            confidence=confidence

        )

    # --------------------------------------------------

    def extract_role(self, text: str) -> Optional[str]:

        slot = self.extract(text)

        if slot:

            return slot.value

        return None