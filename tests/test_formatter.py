from app.retrieval.schema import AssessmentDocument

from app.generation.response import (

    Recommendation,

    GenerationResponse,

)

from app.generation.formatter import ResponseFormatter


doc = AssessmentDocument(

    entity_id="3827",

    name=".NET Framework 4.5",

    description="Measures .NET knowledge.",

    url="https://www.shl.com/products/product-catalog/view/net-framework-45/",

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

    confidence=0.95,

    rank=1

)

response = GenerationResponse(

    answer="Based on your requirements, I recommend the following assessment.",

    recommendations=[recommendation],

    citations=[doc.url]

)

formatter = ResponseFormatter()

final = formatter.format(response)

print("=" * 80)

print(final.message)

print()

print("Verified:", final.verified)

print()

print("Citations")

for c in final.citations:

    print(c)