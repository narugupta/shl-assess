"""
Comparison Item Extractor

Identifies references to specific SHL assessments (by full name or
derived acronym) inside free text, so the COMPARE intent
("what's the difference between OPQ and GSA?") can be grounded
against real catalog entries instead of being stuck asking the user
to repeat themselves forever.

This is name recognition, not retrieval: no scoring, no embeddings,
just matching against the catalog's public names. It loads the same
processed knowledge base the retriever uses, via KnowledgeBaseLoader,
but does none of the retrieval-side indexing/ranking work.
"""

from __future__ import annotations

import re
import threading
from typing import Dict, List, Optional

from app.retrieval.loader import KnowledgeBaseLoader


# Common all-caps tokens that are not assessment acronyms and would
# otherwise create false positives if they happened to collide with
# a catalog alias.
_STOPWORD_ACRONYMS = {
    "I", "A", "OK", "US", "UK", "EU", "IT", "HR", "CEO", "CFO", "CTO",
    "SHL", "AI", "PDF", "URL", "API", "FAQ",
}

# Names this short are too generic to safely substring-match against
# arbitrary free text (e.g. a 2-3 letter product name showing up by
# coincidence inside an unrelated sentence).
_MIN_NAME_LENGTH_FOR_SUBSTRING_MATCH = 4


class ComparisonExtractor:
    """
    Extracts distinct catalog assessment names mentioned in a message.
    """

    _lock = threading.Lock()
    _alias_index: Optional[Dict[str, str]] = None
    _names_longest_first: Optional[List[str]] = None

    def __init__(self):
        self._ensure_index()

    # ------------------------------------------------------------
    # Index construction (built once, shared across instances)
    # ------------------------------------------------------------

    @classmethod
    def _ensure_index(cls) -> None:

        if cls._alias_index is not None:
            return

        with cls._lock:

            if cls._alias_index is not None:
                return

            try:
                documents = KnowledgeBaseLoader().load()
            except FileNotFoundError:
                documents = []

            cls._alias_index, cls._names_longest_first = cls._build_index(
                documents
            )

    @staticmethod
    def _build_index(documents) -> tuple[Dict[str, str], List[str]]:
        """
        Builds:
          - alias_index: lowercase alias (full name or derived
            acronym) -> canonical catalog name
          - names_longest_first: all canonical names, longest first,
            so substring search below prefers the most specific match

        When several catalog entries share the same acronym or
        substring (e.g. many "OPQ ... Report" variants all contain
        "OPQ"), the shortest matching name wins as the canonical
        pick, since it's usually the base assessment rather than a
        report/variant built on top of it.
        """

        alias_index: Dict[str, str] = {}

        # When several catalog entries collide on the same alias
        # (e.g. many "OPQ ... Report" variants all contain "OPQ"),
        # prefer a base assessment over a derived report/profile
        # variant, then fall back to the shortest name.
        raw_names = sorted(
            {doc.name for doc in documents if doc.name},
            key=lambda n: (
                ComparisonExtractor._looks_like_variant(n),
                len(n),
            ),
        )

        for name in raw_names:

            lower = name.lower()

            alias_index.setdefault(lower, name)

            for alias in ComparisonExtractor._derive_aliases(name):
                alias_index.setdefault(alias.lower(), name)

        names_longest_first = sorted(raw_names, key=len, reverse=True)

        return alias_index, names_longest_first

    _VARIANT_WORDS = (
        "report", "profile", "plus", "planner", "development",
        "selection", "impact", "group", "individual", "learning",
    )

    @staticmethod
    def _looks_like_variant(name: str) -> bool:
        """
        True if `name` looks like a report/profile spin-off of a
        base assessment rather than the base assessment itself.
        """

        lower = name.lower()

        return any(word in lower for word in ComparisonExtractor._VARIANT_WORDS)

    _ACRONYM_TOKEN_RE = re.compile(r"[A-Z]{2,}[A-Za-z0-9]*")

    @staticmethod
    def _derive_aliases(name: str) -> List[str]:
        """
        Derives short aliases a user is likely to actually type,
        from two independent sources:

          a) Acronym-like tokens already embedded in the name, e.g.
             "OPQ32r" inside "Occupational Personality Questionnaire
             OPQ32r", plus that token's bare leading-letter run
             ("OPQ32r" -> also "OPQ").

          b) Initials of the name's ordinary Title Case words, e.g.
             "Global Skills Assessment" -> "GSA". Words that are
             already acronym-like tokens (handled by (a)) are
             excluded here so a name that mixes both styles
             (e.g. "...Questionnaire OPQ32r") doesn't get a
             corrupted initials acronym like "OPQO".
        """

        aliases: List[str] = []

        acronym_tokens = ComparisonExtractor._ACRONYM_TOKEN_RE.findall(name)

        for token in acronym_tokens:

            aliases.append(token)

            leading = re.match(r"[A-Z]+", token)

            if leading and leading.group() != token:
                aliases.append(leading.group())

        words = re.findall(r"[A-Za-z][A-Za-z']*", name)

        plain_title_words = [
            w for w in words
            if w[0].isupper()
            and not ComparisonExtractor._ACRONYM_TOKEN_RE.fullmatch(w)
        ]

        if len(plain_title_words) >= 2:

            initials = "".join(w[0] for w in plain_title_words)

            if len(initials) >= 2:
                aliases.append(initials)

        return aliases

    # ------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------

    def extract(self, text: str) -> List[str]:
        """
        Returns catalog assessment names referenced in `text`, in
        order of first mention, without duplicates.
        """

        if not text:
            return []

        matches: List[str] = []
        seen = set()

        # 1) Explicit acronym-like tokens as written, e.g. "OPQ32r",
        #    "GSA", "SJT".
        for token in re.findall(r"\b[A-Z]{2,}[A-Za-z0-9]*\b", text):

            if token.upper() in _STOPWORD_ACRONYMS:
                continue

            canonical = self._alias_index.get(token.lower())

            if canonical and canonical not in seen:
                seen.add(canonical)
                matches.append(canonical)

        # 2) Full/partial catalog names appearing verbatim,
        #    e.g. "compare Java 8 and Python 3 vs C# Programming".
        lower_text = text.lower()

        for name in self._names_longest_first:

            if name in seen:
                continue

            if len(name) < _MIN_NAME_LENGTH_FOR_SUBSTRING_MATCH:
                continue

            if name.lower() in lower_text:
                seen.add(name)
                matches.append(name)

        return matches
