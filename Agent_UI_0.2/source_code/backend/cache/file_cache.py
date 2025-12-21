import hashlib

_cache = set()

def file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

def is_cached(h):
    return h in _cache

def add_cache(h):
    _cache.add(h)
