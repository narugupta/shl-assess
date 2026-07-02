"""
Prompt Templates

Centralized prompt definitions used by the LLM generator.

These prompts are optimized for Retrieval-Augmented Generation (RAG).
The LLM should explain the recommendations, while the frontend
renders the structured assessment cards.
"""

from __future__ import annotations

from enum import Enum


# ============================================================
# Prompt Types
# ============================================================

class PromptType(str, Enum):

    RECOMMEND = "recommend"

    COMPARE = "compare"

    JOB_DESCRIPTION = "job_description"

    CLARIFICATION = "clarification"

    REFINE = "refine"


# ============================================================
# System Prompt
# ============================================================

SYSTEM_PROMPT = """
You are an expert SHL Assessment Recommendation Assistant.

Answer ONLY using the retrieved assessment context.

STRICT RULES

1. Never invent assessment names.
2. Never invent URLs.
3. Never invent durations.
4. Never invent languages.
5. Never invent job levels.
6. Never invent categories.
7. Never recommend assessments not present in the retrieved context.
8. If the retrieved information is insufficient, clearly state that.
9. Keep responses concise and professional.
10. Explain WHY the retrieved assessments satisfy the user's request.
11. The application displays structured assessment details separately.
12. Avoid repeating metadata already shown by the application.
13. Do not use Markdown headings unless explicitly requested.
14. Prefer one or two concise paragraphs.
"""


# ============================================================
# Recommendation Prompt
# ============================================================

RECOMMEND_TEMPLATE = """
User Request
------------
{query}

Retrieved Assessments
---------------------
{context}

Task
----
The assessments have already been selected by the retrieval system.

Your job is ONLY to explain why these assessments are appropriate.

Explain:

- how the retrieved assessments satisfy the hiring requirement
- what skills or competencies they collectively evaluate
- any important trade-offs if applicable

Do NOT:

- repeat the assessment list
- enumerate assessments
- repeat durations
- repeat URLs
- repeat languages
- repeat job levels
- repeat categories

The application will render the assessment cards separately.

Keep the response under 120 words.

Use ONLY the retrieved context.
"""


# ============================================================
# Comparison Prompt
# ============================================================

COMPARE_TEMPLATE = """
User Request
------------
{query}

Retrieved Assessments
---------------------
{context}

Task
----
Compare the requested assessments.

Discuss:

- purpose
- competencies measured
- ideal hiring scenarios
- important strengths
- important differences

Keep the comparison factual.

Use ONLY the retrieved context.
"""


# ============================================================
# Job Description Prompt
# ============================================================

JOB_DESCRIPTION_TEMPLATE = """
Job Description
---------------
{query}

Retrieved Assessments
---------------------
{context}

Task
----
Explain why the retrieved assessments fit this job description.

Discuss:

- which requirements they evaluate
- why they are appropriate
- how they complement each other

Avoid repeating structured metadata.

Use ONLY the retrieved context.
"""


# ============================================================
# Clarification Prompt
# ============================================================

CLARIFICATION_TEMPLATE = """
Conversation
------------
{query}

Task
----
The user's request is incomplete.

Ask ONE short clarification question.

Do not ask multiple questions.

Do not explain your reasoning.
"""


# ============================================================
# Refinement Prompt
# ============================================================

REFINE_TEMPLATE = """
Conversation
------------
{query}

Current Recommendations
-----------------------
{context}

Task
----
Update the recommendations according to the user's refinement.

Only adjust the explanation based on the retrieved assessments.

Do not introduce new assessments.

Keep the response brief.

Use ONLY the retrieved context.
"""


# ============================================================
# Prompt Manager
# ============================================================

class PromptManager:
    """
    Builds prompts for the requested task.
    """

    def __init__(self):

        self.system_prompt = SYSTEM_PROMPT

    # ---------------------------------------------------------

    def get_system_prompt(self) -> str:

        return self.system_prompt

    # ---------------------------------------------------------

    def build_prompt(
        self,
        prompt_type: PromptType,
        query: str,
        context: str = "",
    ) -> str:

        templates = {

            PromptType.RECOMMEND: RECOMMEND_TEMPLATE,

            PromptType.COMPARE: COMPARE_TEMPLATE,

            PromptType.JOB_DESCRIPTION: JOB_DESCRIPTION_TEMPLATE,

            PromptType.CLARIFICATION: CLARIFICATION_TEMPLATE,

            PromptType.REFINE: REFINE_TEMPLATE,

        }

        if prompt_type not in templates:

            raise ValueError(
                f"Unknown prompt type: {prompt_type}"
            )

        return templates[prompt_type].format(

            query=query,

            context=context,

        )