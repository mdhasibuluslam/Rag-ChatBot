_query_cache = {}

def get_query_embedding(q):
    return _query_cache.get(q)

def set_query_embedding(q, emb):
    _query_cache[q] = emb
