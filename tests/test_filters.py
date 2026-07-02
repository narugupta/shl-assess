from app.retrieval.loader import KnowledgeBaseLoader
from app.retrieval.preprocess import KnowledgeBasePreprocessor
from app.retrieval.embedder import EmbeddingGenerator
from app.retrieval.faiss_index import FAISSIndex
from app.retrieval.bm25_index import BM25Index
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.filters import CandidateFilter
from app.retrieval.schema import RetrievalQuery

loader = KnowledgeBaseLoader()

docs = loader.load()

processor = KnowledgeBasePreprocessor()

docs = processor.preprocess(docs)

embedder = EmbeddingGenerator()

embeddings = embedder.encode_documents(docs)

faiss = FAISSIndex()

faiss.build(embeddings, docs)

bm25 = BM25Index()

bm25.build(docs)

hybrid = HybridRetriever(

    bm25,

    faiss,

    embedder

)

results = hybrid.search(

    "Java Developer",

    top_k=20

)

print("Before filtering:", len(results))

query = RetrievalQuery(

    language="English (USA)",

    seniority="Mid-Professional",

    duration=30,

    duration_operator="lte",

    categories=[

        "Knowledge & Skills"

    ]

)

filter_engine = CandidateFilter()

filtered = filter_engine.filter(

    results,

    query

)

print("After filtering:", len(filtered))

print()

for r in filtered:

    print(

        r.document.name,

        r.document.duration,

        r.document.languages,

        r.document.job_levels,

        r.document.categories

    )