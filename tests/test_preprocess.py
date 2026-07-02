from app.retrieval.loader import KnowledgeBaseLoader
from app.retrieval.preprocess import KnowledgeBasePreprocessor

loader = KnowledgeBaseLoader()

documents = loader.load()

processor = KnowledgeBasePreprocessor()

documents = processor.preprocess(documents)

print()

print(documents[0].name)

print()

print(documents[0].search_text)

print()

print("Length:", len(documents[0].search_text))