from app.api.pipeline import RecommendationPipeline
from app.api.models import RecommendRequest

pipeline = RecommendationPipeline()

request = RecommendRequest(

    query="Need Java Developer assessment in English under 30 minutes",

    top_k=5,

)

response = pipeline.recommend(

    request

)

print()

print("=" * 80)

print("MESSAGE")

print("=" * 80)

print(response.message)

print()

print("=" * 80)

print("RECOMMENDATIONS")

print("=" * 80)

for rec in response.recommendations:

    print(

        rec.rank,

        rec.name,

        rec.duration,

        rec.languages,

        rec.confidence,

    )

print()

print("=" * 80)

print("VERIFIED")

print("=" * 80)

print(response.verified)