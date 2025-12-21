#!/usr/bin/env python3
"""Test end-to-end pipeline: create sample docs, upload, search, retrieve."""
import os
import sys
os.chdir(r'E:\Agent_UI_0.1\backend')
sys.path.insert(0, r'E:\Agent_UI_0.1\backend')

from vectorstore.faiss_store import FaissStore
from vectorstore.embedder import embed
import faiss
import pickle
import numpy as np

# Create sample index with test documents
def setup_test_index():
    print("\n=== Creating test FAISS index ===")
    docs = [
        {"source": "test1.txt", "text": "Machine learning is a subset of artificial intelligence."},
        {"source": "test1.txt", "text": "AI can learn patterns from data without explicit programming."},
        {"source": "test2.txt", "text": "Deep learning uses neural networks with multiple layers."},
        {"source": "test2.txt", "text": "Natural language processing helps computers understand human language."},
    ]
    
    texts = [d["text"] for d in docs]
    embeddings = embed(texts)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, "data/index.faiss")
    with open("data/meta.pkl", "wb") as f:
        pickle.dump(docs, f)
    
    print(f"Created index with {len(docs)} documents")
    return docs

# Test search
def test_search(docs):
    print("\n=== Testing search ===")
    store = FaissStore()
    
    queries = [
        "What is machine learning?",
        "Tell me about neural networks",
        "How does NLP work?",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = store.search(query, top_k=2)
        print(f"Found {len(results)} results:")
        for i, res in enumerate(results, 1):
            print(f"  {i}. [score={res['score']:.4f}] {res['text'][:80]}...")
            
if __name__ == "__main__":
    docs = setup_test_index()
    test_search(docs)
    print("\n✓ Pipeline test complete!")
