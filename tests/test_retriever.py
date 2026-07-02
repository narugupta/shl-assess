from app.retrieval.retriever import Retriever
from app.retrieval.schema import RetrievalQuery

retriever = Retriever()

query = RetrievalQuery(

    role="Java Developer",

    language="English (USA)",

    seniority="Mid-Professional",

    duration=30,

    duration_operator="lte",

    categories=["Knowledge & Skills"],

    free_text="Need Java Developer assessment"

)

results = retriever.retrieve(

    query,

    top_k=5

)

print()

print("=" * 70)

print("Retrieved Results")

print("=" * 70)

for rank, candidate in enumerate(results.candidates, start=1):

    doc = candidate.document

    print()

    print(f"{rank}. {doc.name}")

    print("Score:", round(candidate.score, 3))

    print("Duration:", doc.duration)

    print("Languages:", doc.languages)

    print("Categories:", doc.categories)

    print("URL:", doc.url)