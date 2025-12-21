import faiss
import pickle
import os
import logging
import numpy as np
from vectorstore.embedder import embed

logger = logging.getLogger(__name__)

class FaissStore:
    def __init__(self):
        self.index = None
        self.meta = None
        self.loaded = False

    def load(self):
        if self.loaded:
            return
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        index_path = os.path.join(base_dir, "data", "index.faiss")
        meta_path = os.path.join(base_dir, "data", "meta.pkl")

        if not os.path.exists(index_path):
            logger.error("Faiss index not found at %s", index_path)
            self.index = None
            self.meta = None
            self.loaded = True
            return

        # try normal load first, then fallback to mmap if MemoryError or other failures
        try:
            self.index = faiss.read_index(index_path)
        except MemoryError as me:
            logger.warning("faiss.read_index raised MemoryError, trying mmap: %s", me)
            try:
                self.index = faiss.read_index(index_path, faiss.IO_FLAG_MMAP)
            except Exception:
                logger.exception("faiss.read_index mmap fallback also failed")
                self.index = None
        except Exception:
            logger.exception("faiss.read_index failed, attempting mmap fallback")
            try:
                self.index = faiss.read_index(index_path, faiss.IO_FLAG_MMAP)
            except Exception:
                logger.exception("faiss.read_index mmap fallback failed")
                self.index = None

        # load meta if available
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "rb") as f:
                    self.meta = pickle.load(f)
            except Exception:
                logger.exception("Failed to load meta.pkl")
                self.meta = None
        else:
            logger.error("meta.pkl not found at %s", meta_path)
            self.meta = None

        self.loaded = True
   
    def search(self, vector_or_text, top_k=5):
        """Accept either a precomputed embedding (np.ndarray) or a query string.

        Returns a list of docs: [{'text': ..., 'score': ...}, ...]
        """
        self.load()

        if self.index is None:
            logger.warning("Search requested but Faiss index is not loaded")
            return []

        # if user passed a raw text query, compute embedding
        if isinstance(vector_or_text, str):
            vec = embed([vector_or_text])
            # SentenceTransformer returns a 2D array
            query_vec = np.array([vec[0]], dtype=np.float32)
        else:
            # assume it's an array-like embedding
            query_vec = np.array(vector_or_text, dtype=np.float32)
            if query_vec.ndim == 1:
                query_vec = query_vec.reshape(1, -1)

        # perform search (L2 distance; lower is better)
        try:
            D, I = self.index.search(query_vec, top_k)
        except Exception as e:
            logger.exception("Faiss search failed")
            return []

        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx < 0:
                continue
            try:
                if self.meta and idx < len(self.meta):
                    item = self.meta[idx]
                    if isinstance(item, dict):
                        text = item.get("text") or item.get("content") or str(item)
                    else:
                        text = str(item)
                else:
                    text = ""
            except Exception:
                text = ""

            results.append({"text": text, "score": float(dist)})

        return results
