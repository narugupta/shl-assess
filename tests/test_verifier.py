from app.retrieval.schema import AssessmentDocument

from app.generation.response import (

    Recommendation,

    GenerationResponse,

)

from app.generation.verifier import ResponseVerifier


doc = AssessmentDocument(

    entity_id="1",

    name="Java Programming",

    description="",

    url="https://www.shl.com/java",

    duration=30,

    languages=["English (USA)"],

    job_levels=["Mid-Professional"],

    categories=["Knowledge & Skills"],

    remote=True,

    adaptive=False,

)

recommendation = Recommendation(

    document=doc,

    reason="Matches Java skills.",

)

# ----------------------------------------

good = GenerationResponse(

    recommendations=[recommendation],

    answer="""
I recommend **Java Programming**.

Duration: 30 minutes.

URL:
https://www.shl.com/java
"""

)

# ----------------------------------------

bad = GenerationResponse(

    recommendations=[recommendation],

    answer="""
I recommend **Python Advanced**.

https://fakeurl.com
"""

)

verifier = ResponseVerifier()

print("=" * 60)

print("GOOD RESPONSE")

print(verifier.verify(good))

print()

print("=" * 60)

print("BAD RESPONSE")

print(verifier.verify(bad))