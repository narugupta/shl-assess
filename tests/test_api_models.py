from pprint import pprint

from app.api.models import (

    RecommendRequest,

    RecommendResponse,

    AssessmentRecommendation,

    HealthResponse,

)

request = RecommendRequest(

    query="Need Java Developer assessment",

    top_k=5,

)

print()

print("Request")

pprint(

    request.model_dump()

)

recommendation = AssessmentRecommendation(

    rank=1,

    name="Java Programming",

    url="https://www.shl.com/java",

    duration=30,

    languages=["English (USA)"],

    job_levels=["Mid-Professional"],

    categories=["Knowledge & Skills"],

    confidence=0.94,

    reason="Matches Java programming requirements."

)

response = RecommendResponse(

    message="Recommendations generated.",

    recommendations=[recommendation],

    citations=[

        "https://www.shl.com/java"

    ],

)

print()

print("Response")

pprint(

    response.model_dump()

)

health = HealthResponse(

    status="healthy",

    version="1.0.0",

    planner_ready=True,

    retriever_ready=True,

    generator_ready=True,

)

print()

print("Health")

pprint(

    health.model_dump()

)