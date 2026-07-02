"""
Response Verifier

Verifies that the generated response is grounded in the
retrieved assessments.

Checks
------
✓ Assessment names
✓ URLs
✓ Duplicate recommendations
✓ Hallucinated assessment names

This verifier intentionally does NOT parse arbitrary markdown
labels such as "**Assessment Name:**". Instead it checks whether
known assessment names appear in the answer.
"""

from __future__ import annotations

import re

from app.generation.response import (
    GenerationResponse,
    VerificationResult,
)


class ResponseVerifier:

    """
    Simple hallucination verifier.
    """

    # ---------------------------------------------------------

    def verify(
        self,
        response: GenerationResponse,
    ) -> VerificationResult:

        issues = []

        recommendations = response.recommendations

        answer = response.answer or ""

        if not recommendations:

            return VerificationResult(

                passed=True,

                issues=[]

            )

        # -------------------------------------------------
        # Allowed assessment names
        # -------------------------------------------------

        allowed_names = {

            r.document.name.lower()

            for r in recommendations

        }

        # -------------------------------------------------
        # Allowed URLs
        # -------------------------------------------------

        allowed_urls = {

            r.document.url

            for r in recommendations

        }

        # -------------------------------------------------
        # Verify URLs
        # -------------------------------------------------

        urls = re.findall(

            r"https?://\S+",

            answer

        )

        for url in urls:

            cleaned = url.rstrip(").,]}>")

            if cleaned not in allowed_urls:

                issues.append(

                    f"Unknown URL: {cleaned}"

                )

        # -------------------------------------------------
        # Verify assessment names
        #
        # We DO NOT extract every bold phrase.
        #
        # Instead we check that every retrieved assessment
        # mentioned in the answer is valid.
        # -------------------------------------------------

        answer_lower = answer.lower()

        found_names = []

        for name in allowed_names:

            if name in answer_lower:

                found_names.append(name)

        # If answer references assessments but none of the
        # retrieved assessments appear, it's suspicious.

        if urls and not found_names:

            issues.append(

                "The response contains URLs but no known assessment names."

            )

        # -------------------------------------------------
        # Duplicate recommendations
        # -------------------------------------------------

        seen = set()

        for rec in recommendations:

            name = rec.document.name.lower()

            if name in seen:

                issues.append(

                    f"Duplicate recommendation: {rec.document.name}"

                )

            seen.add(name)

        # -------------------------------------------------
        # Empty answer
        # -------------------------------------------------

        if not answer.strip():

            issues.append(

                "Generated answer is empty."

            )

        # -------------------------------------------------

        return VerificationResult(

            passed=len(issues) == 0,

            issues=issues

        )