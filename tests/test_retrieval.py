"""
End-to-End Retrieval Test

Runs the complete retrieval pipeline.

Knowledge Base
    ↓
Preprocessor
    ↓
Embeddings
    ↓
FAISS
    ↓
BM25
    ↓
Hybrid Retrieval
    ↓
Filtering
    ↓
Ranking
"""

from pprint import pprint

from app.retrieval.retriever import Retriever
from app.retrieval.schema import RetrievalQuery


def print_result(result):

    print("\n" + "=" * 80)

    print("Query")

    pprint(result.query)

    print()

    print(f"Retrieved {len(result.candidates)} assessments")

    print("=" * 80)

    if not result.candidates:

        print("No results found.")

        return

    for rank, candidate in enumerate(result.candidates, start=1):

        doc = candidate.document

        print(f"\n#{rank}")

        print(f"Name       : {doc.name}")

        print(f"Score      : {candidate.score:.3f}")

        print(f"Duration   : {doc.duration}")

        print(f"Languages  : {doc.languages}")

        print(f"Job Levels : {doc.job_levels}")

        print(f"Categories : {doc.categories}")

        print(f"Remote     : {doc.remote}")

        print(f"Adaptive   : {doc.adaptive}")

        print(f"URL        : {doc.url}")

        print(f"Metadata   : {candidate.metadata}")


def main():

    retriever = Retriever()

    queries = [

        RetrievalQuery(

            role="Java Developer",

            seniority="Mid-Professional",

            language="English (USA)",

            categories=["Knowledge & Skills"],

            duration=30,

            duration_operator="lte",

            free_text="Need Java Developer assessment"

        ),

        RetrievalQuery(

            role=".NET Developer",

            language="English (USA)",

            categories=["Knowledge & Skills"],

            free_text=".NET assessment"

        ),

        RetrievalQuery(

            role="Finance Analyst",

            language="English (USA)",

            free_text="Finance Analyst"

        ),

        RetrievalQuery(

            role="Leadership",

            categories=["Personality & Behavior"],

            free_text="Leadership assessment"

        )

    ]

    for query in queries:

        result = retriever.retrieve(

            query,

            top_k=5

        )

        print_result(result)


if __name__ == "__main__":

    main()