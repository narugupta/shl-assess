from app.retrieval.loader import KnowledgeBaseLoader
from app.retrieval.preprocess import KnowledgeBasePreprocessor
from app.retrieval.embedder import EmbeddingGenerator
from app.retrieval.faiss_index import FAISSIndex
from app.retrieval.bm25_index import BM25Index
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.filters import CandidateFilter
from app.retrieval.ranker import CandidateRanker
from app.retrieval.schema import RetrievalQuery

loader = KnowledgeBaseLoader()

documents = loader.load()

documents = KnowledgeBasePreprocessor().preprocess(documents)

embedder = EmbeddingGenerator()

embeddings = embedder.encode_documents(documents)

faiss = FAISSIndex()

faiss.build(embeddings, documents)

bm25 = BM25Index()

bm25.build(documents)

hybrid = HybridRetriever(

    bm25,

    faiss,

    embedder

)

query = RetrievalQuery(

    role="Java Developer",

    language="English (USA)",

    seniority="Mid-Professional",

    duration=30,

    duration_operator="lte",

    categories=["Knowledge & Skills"],

    free_text="Need Java developer assessment"

)

results = hybrid.search(

    query.role,

    top_k=20

)

results = CandidateFilter().filter(

    results,

    query

)

results = CandidateRanker().rerank(

    results,

    query

)

print()

print("Top Results")

print()

for i, r in enumerate(results[:10], start=1):

    print(

        i,

        r.document.name,

        round(r.score, 3),

        r.metadata

    )