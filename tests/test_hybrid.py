from app.retrieval.loader import KnowledgeBaseLoader
from app.retrieval.preprocess import KnowledgeBasePreprocessor
from app.retrieval.embedder import EmbeddingGenerator
from app.retrieval.faiss_index import FAISSIndex
from app.retrieval.bm25_index import BM25Index
from app.retrieval.hybrid import HybridRetriever

loader = KnowledgeBaseLoader()

documents = loader.load()

processor = KnowledgeBasePreprocessor()

documents = processor.preprocess(documents)

embedder = EmbeddingGenerator()

embeddings = embedder.encode_documents(documents)

# Build FAISS
faiss = FAISSIndex()

faiss.build(
    embeddings,
    documents
)

# Build BM25
bm25 = BM25Index()

bm25.build(documents)

# Hybrid
hybrid = HybridRetriever(

    bm25=bm25,

    faiss=faiss,

    embedder=embedder,

)

queries = [

    "Java Developer",

    ".NET",

    "Leadership",

    "SQL",

    "Personality",

]

for query in queries:

    print("=" * 70)

    print("Query:", query)

    results = hybrid.search(
        query,
        top_k=5
    )

    for i, result in enumerate(results, 1):

        print(

            f"{i}.",

            result.document.name,

            "|",

            round(result.score, 3),

            "|",

            result.metadata

        )