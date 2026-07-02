from app.retrieval.loader import KnowledgeBaseLoader
from app.retrieval.preprocess import KnowledgeBasePreprocessor
from app.retrieval.bm25_index import BM25Index

loader = KnowledgeBaseLoader()

documents = loader.load()

processor = KnowledgeBasePreprocessor()

documents = processor.preprocess(documents)

index = BM25Index()

index.build(documents)

print()

print("Indexed:", len(index))

print()

queries = [

    "Java Developer",

    ".NET",

    "Python",

    "SQL",

    "Personality",

    "Leadership",

]

for query in queries:

    print("=" * 70)

    print("Query:", query)

    results = index.search(query, top_k=5)

    if not results:

        print("No results")

        continue

    for rank, result in enumerate(results, start=1):

        print(

            rank,

            "|",

            round(result.score, 2),

            "|",

            result.document.name

        )