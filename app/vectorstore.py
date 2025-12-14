import chromadb
from embedding import get_embedder

# NEW ChromaDB Client (v0.5+)
client = chromadb.PersistentClient(path="./data/chroma")

# Create or load collection
collection = client.get_or_create_collection("docs")

def add_docs(ids, docs):
    embeddings = [get_embedder(d) for d in docs]
    collection.add(ids=ids, documents=docs, embeddings=embeddings)

def query_docs(query, n_results=3):
    q_emb = get_embedder(query)
    result = collection.query(query_embeddings=[q_emb], n_results=n_results)
    return result["documents"][0]
