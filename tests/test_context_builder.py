from app.generation.context_builder import ContextBuilder
from app.generation.response import Recommendation
from app.retrieval.schema import AssessmentDocument

doc = AssessmentDocument(

    entity_id="3827",

    name=".NET Framework 4.5",

    description="Measures knowledge of the Microsoft .NET Framework.",

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

    confidence=0.94,

    rank=1

)

builder = ContextBuilder()

context = builder.build([recommendation])

print("=" * 80)

print("Context")

print("=" * 80)

print(context)

print()

system_prompt = builder.build_system_prompt(context)

print("=" * 80)

print("System Prompt")

print("=" * 80)

print(system_prompt)

print()

user_prompt = builder.build_user_prompt(

    "Need a .NET assessment"

)

print("=" * 80)

print("User Prompt")

print("=" * 80)

print(user_prompt)