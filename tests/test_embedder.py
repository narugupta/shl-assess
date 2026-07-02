from app.retrieval.loader import KnowledgeBaseLoader
from app.retrieval.preprocess import KnowledgeBasePreprocessor
from app.retrieval.embedder import EmbeddingGenerator

loader = KnowledgeBaseLoader()

docs = loader.load()

processor = KnowledgeBasePreprocessor()

docs = processor.preprocess(docs)

embedder = EmbeddingGenerator()

embeddings = embedder.encode_documents(docs)

print()

print("Documents:", len(docs))

print("Embedding shape:", embeddings.shape)

print("Dimension:", embedder.embedding_dimension())

print()

query = embedder.encode_query(
    "Java Backend Developer"
)

print("Query shape:", query.shape)

print()

embedder.save_embeddings(
    embeddings,
    "data/processed/embeddings.npy"
)

print("Saved embeddings.")