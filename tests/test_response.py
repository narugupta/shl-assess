from pprint import pprint

from app.retrieval.schema import AssessmentDocument

from app.generation.response import (

    Recommendation,

    GenerationResponse,

    recommendation_summary,

    response_summary,

)

doc = AssessmentDocument(

    entity_id="3827",

    name=".NET Framework 4.5",

    description="Measures .NET knowledge.",

    url="https://www.shl.com/",

    duration=30,

    languages=["English (USA)"],

    job_levels=["Mid-Professional"],

    categories=["Knowledge & Skills"],

    remote=True,

    adaptive=True,

)

recommendation = Recommendation(

    document=doc,

    reason="Matches the requested .NET skills.",

    confidence=0.94,

    rank=1

)

response = GenerationResponse(

    recommendations=[recommendation],

    answer="I recommend the following assessment.",

    citations=[doc.url]

)

print()

print("Recommendation")

pprint(

    recommendation_summary(

        recommendation

    )

)

print()

print("Response")

pprint(

    response_summary(

        response

    )

)