from pprint import pprint

from app.retrieval.loader import KnowledgeBaseLoader

loader = KnowledgeBaseLoader()

documents = loader.load()

print()

print("Documents:", len(documents))

print()

first = documents[0]

print(first)

print()

print(first.metadata)

print()

pprint(first.categories)