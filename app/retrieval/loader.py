"""
Knowledge Base Loader

Loads the processed SHL knowledge base and converts every
assessment into an AssessmentDocument.

No indexing happens here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.retrieval.schema import AssessmentDocument


class KnowledgeBaseLoader:

    def __init__(self, knowledge_base_path: str | None = None):

        if knowledge_base_path is None:

            root = Path(__file__).resolve().parents[2]

            knowledge_base_path = (
                root
                / "data"
                / "processed"
                / "knowledge_base.json"
            )

        self.path = Path(knowledge_base_path)

    # -----------------------------------------------------

    def load(self) -> List[AssessmentDocument]:

        if not self.path.exists():

            raise FileNotFoundError(

                f"Knowledge base not found:\n{self.path}"

            )

        with open(

            self.path,

            "r",

            encoding="utf-8"

        ) as f:

            data = json.load(f)

        documents = []

        for item in data:

            documents.append(

                self._parse_document(item)

            )

        return documents

    # -----------------------------------------------------

    def _parse_document(

        self,

        item: dict

    ) -> AssessmentDocument:

        return AssessmentDocument(

            entity_id=item.get("entity_id", ""),

            name=item.get("name", ""),

            description=item.get("description", ""),

            url=item.get("link", ""),

            duration=self._parse_duration(

                item.get("duration", "")

            ),

            languages=item.get("languages", []),

            job_levels=item.get("job_levels", []),

            categories=item.get("keys", []),

            remote=self._parse_bool(

                item.get("remote", "no")

            ),

            adaptive=self._parse_bool(

                item.get("adaptive", "no")

            ),

            metadata={

                "status": item.get("status"),

                "scraped_at": item.get("scraped_at"),

                "duration_raw": item.get("duration_raw"),

                "languages_raw": item.get("languages_raw"),

                "job_levels_raw": item.get("job_levels_raw"),

            }

        )

    # -----------------------------------------------------

    @staticmethod
    def _parse_bool(value) -> bool:

        if isinstance(value, bool):

            return value

        if value is None:

            return False

        return str(value).lower() == "yes"

    # -----------------------------------------------------

    @staticmethod
    def _parse_duration(value):

        """
        Convert

        "30 minutes"

        into

        30
        """

        if value is None:

            return None

        if isinstance(value, int):

            return value

        value = str(value).strip()

        if not value:

            return None

        digits = ""

        for c in value:

            if c.isdigit():

                digits += c

        if digits:

            return int(digits)

        return None

    # -----------------------------------------------------

    def count(self) -> int:

        return len(self.load())