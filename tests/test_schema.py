from pprint import pprint

from app.retrieval.schema import (
    AssessmentDocument,
    RetrievalQuery,
    RetrievalCandidate,
    document_summary,
    candidate_summary,
)

doc = AssessmentDocument(

    entity_id="3827",

    name=".NET Framework 4.5",

    description="Measures knowledge of .NET.",

    url="https://example.com",

    duration=30,

    languages=["English (USA)"],

    job_levels=["Mid-Professional"],

    categories=["Knowledge & Skills"],

    remote=True,

    adaptive=False,

)

query = RetrievalQuery(

    role=".NET Developer",

    seniority="Mid-Professional",

    language="English (USA)",

    duration=30,

    skills=[".NET"]

)

candidate = RetrievalCandidate(

    document=doc,

    score=0.87,

    source="bm25"

)

print()

print("DOCUMENT")

pprint(document_summary(doc))

print()

print("QUERY")

pprint(query)

print()

print("CANDIDATE")

pprint(candidate_summary(candidate))