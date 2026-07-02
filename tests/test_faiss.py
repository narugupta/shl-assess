from app.retrieval.loader import KnowledgeBaseLoader
from app.retrieval.preprocess import KnowledgeBasePreprocessor
from app.retrieval.embedder import EmbeddingGenerator
from app.retrieval.faiss_index import FAISSIndex

loader = KnowledgeBaseLoader()

documents = loader.load()

processor = KnowledgeBasePreprocessor()

documents = processor.preprocess(documents)

embedder = EmbeddingGenerator()

embeddings = embedder.encode_documents(documents)

index = FAISSIndex()

index.build(
    embeddings,
    documents
)

print()

print("Documents indexed:", index.ntotal())

print()

query = embedder.encode_query(
    "Java Developer programming assessment"
)

results = index.search(
    query,
    top_k=5
)

for i, result in enumerate(results, start=1):

    print("=" * 60)

    print(f"Rank {i}")

    print("Score:", round(result.score, 4))

    print("Assessment:", result.document.name)

    print("Categories:", result.document.categories)

    print("Duration:", result.document.duration)