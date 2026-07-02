"""
End-to-End Integration Test

Tests the complete recommendation pipeline.

Planner
↓

Retriever
↓

Context Builder
↓

Groq LLM

↓

Verifier

↓

Formatter
"""

from app.planner.planner import Planner

from app.retrieval.retriever import Retriever
from app.retrieval.schema import RetrievalQuery

from app.generation.context_builder import ContextBuilder
from app.generation.generator import LLMGenerator
from app.generation.verifier import ResponseVerifier
from app.generation.formatter import ResponseFormatter


def build_query(state):

    return RetrievalQuery(

        role=state.role,

        seniority=state.seniority,

        language=state.language,

        duration=state.duration,

        duration_operator=getattr(

            state,

            "duration_operator",

            None

        ),

        categories=state.categories,

        skills=state.skills,

        free_text=" ".join(

            state.history_summary

        )

    )


def main():

    conversation = [

        {

            "role":"user",

            "content":"Need Java Developer assessment"

        },

        {

            "role":"assistant",

            "content":"What experience level?"

        },

        {

            "role":"user",

            "content":"Mid level"

        },

        {

            "role":"assistant",

            "content":"Language?"

        },

        {

            "role":"user",

            "content":"English (USA)"

        },

        {

            "role":"assistant",

            "content":"Maximum duration?"

        },

        {

            "role":"user",

            "content":"Under 30 minutes"

        }

    ]

    # -------------------------------------------------

    print()

    print("=" * 80)

    print("PLANNER")

    print("=" * 80)

    planner = Planner()

    planner_result = planner.plan(

        conversation

    )

    state = planner_result.state

    print(state.summary())

    # -------------------------------------------------

    print()

    print("=" * 80)

    print("RETRIEVAL")

    print("=" * 80)

    query = build_query(state)

    retriever = Retriever()

    retrieval = retriever.retrieve(

        query,

        top_k=5

    )

    print(

        "Retrieved",

        len(retrieval.candidates),

        "documents"

    )

    # -------------------------------------------------

    print()

    print("=" * 80)

    print("CONTEXT")

    print("=" * 80)

    recommendations = []

    for rank, candidate in enumerate(

        retrieval.candidates,

        start=1

    ):

        from app.generation.response import Recommendation

        recommendations.append(

            Recommendation(

                document=candidate.document,

                rank=rank,

                confidence=candidate.score,

                reason="Retrieved by hybrid search"

            )

        )

    builder = ContextBuilder()

    context = builder.build(

        recommendations

    )

    print(

        context[:800]

    )

    # -------------------------------------------------

    print()

    print("=" * 80)

    print("LLM")

    print("=" * 80)

    generator = LLMGenerator()

    response = generator.recommend(

        query=query.free_text,

        context=context

    )

    response.recommendations = recommendations

    response.citations = [

        r.document.url

        for r in recommendations

    ]

    print(

        response.answer

    )

    # -------------------------------------------------

    print()

    print("=" * 80)

    print("VERIFICATION")

    print("=" * 80)

    verifier = ResponseVerifier()

    verification = verifier.verify(

        response

    )

    print(

        verification

    )

    # -------------------------------------------------

    print()

    print("=" * 80)

    print("FORMATTER")

    print("=" * 80)

    formatter = ResponseFormatter()

    final = formatter.format(

        response

    )

    print(

        final.message

    )

    print()

    print("=" * 80)

    print("PIPELINE COMPLETE")

    print("=" * 80)


if __name__ == "__main__":

    main()