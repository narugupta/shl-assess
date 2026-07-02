"""
LLM Generator

Uses the Groq API to generate grounded responses from
retrieved SHL assessments.

Pipeline

Context Builder
        │
        ▼
Prompt Manager
        │
        ▼
Groq LLM
        │
        ▼
GenerationResponse
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

from app.generation.prompts import (
    PromptManager,
    PromptType,
)

from app.generation.response import (
    GenerationResponse,
)

load_dotenv()


class LLMGenerator:

    def __init__(self):

        self.client = OpenAI(

            api_key=os.getenv("GROQ_API_KEY"),

            base_url="https://api.groq.com/openai/v1",

        )

        self.model = os.getenv(

            "GROQ_MODEL",

            "llama-3.3-70b-versatile"

        )

        self.prompts = PromptManager()

    # --------------------------------------------------

    def generate(

        self,

        prompt_type: PromptType,

        query: str,

        context: str,

    ) -> GenerationResponse:

        """
        Generate a grounded response.
        """

        system_prompt = self.prompts.get_system_prompt()

        user_prompt = self.prompts.build_prompt(

            prompt_type,

            query,

            context

        )

        completion = self.client.chat.completions.create(

            model=self.model,

            temperature=0.2,

            max_tokens=1024,

            messages=[

                {

                    "role": "system",

                    "content": system_prompt

                },

                {

                    "role": "user",

                    "content": user_prompt

                }

            ]

        )

        answer = completion.choices[0].message.content.strip()

        return GenerationResponse(

            answer=answer

        )

    # --------------------------------------------------

    def recommend(

        self,

        query: str,

        context: str,

    ) -> GenerationResponse:

        return self.generate(

            PromptType.RECOMMEND,

            query,

            context

        )

    # --------------------------------------------------

    def compare(

        self,

        query: str,

        context: str,

    ) -> GenerationResponse:

        return self.generate(

            PromptType.COMPARE,

            query,

            context

        )

    # --------------------------------------------------

    def analyze_job_description(

        self,

        job_description: str,

        context: str,

    ) -> GenerationResponse:

        return self.generate(

            PromptType.JOB_DESCRIPTION,

            job_description,

            context

        )

    # --------------------------------------------------

    def clarify(

        self,

        query: str,

    ) -> GenerationResponse:

        return self.generate(

            PromptType.CLARIFICATION,

            query,

            ""

        )

    # --------------------------------------------------

    def refine(

        self,

        query: str,

        context: str,

    ) -> GenerationResponse:

        return self.generate(

            PromptType.REFINE,

            query,

            context

        )