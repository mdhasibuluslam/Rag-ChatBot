from sentence_transformers import SentenceTransformer

model = 'all-MiniLM-L6-v2'
embedder = SentenceTransformer(model)

def get_embedder(text:str):
    return embedder.encode(text).tolist()

