from fastapi import APIRouter, UploadFile, File
import os
import pickle
import faiss
import numpy as np
import logging
import tempfile
from ingestion import pdf, docx, pptx, text, json_file, image_ocr
from chunking.chunker import chunk_text
from vectorstore.embedder import embed
from cache.file_cache import file_hash, is_cached, add_cache

logger = logging.getLogger(__name__)
router = APIRouter()


def get_index_paths():
    """Get paths for FAISS index and metadata."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return {
        "index": os.path.join(base_dir, "data", "index.faiss"),
        "meta": os.path.join(base_dir, "data", "meta.pkl")
    }


def load_or_create_index():
    """Load existing FAISS index or create a new one."""
    paths = get_index_paths()
    
    if os.path.exists(paths["index"]) and os.path.exists(paths["meta"]):
        try:
            index = faiss.read_index(paths["index"])
            with open(paths["meta"], "rb") as f:
                meta = pickle.load(f)
            logger.info("Loaded existing FAISS index with %d docs", len(meta))
            return index, meta
        except Exception as e:
            logger.warning("Failed to load existing index: %s; creating new", e)
    
    # Create a new flat L2 index with 384 dims (all-MiniLM-L6-v2 embedding size)
    index = faiss.IndexFlatL2(384)
    meta = []
    logger.info("Created new FAISS index")
    return index, meta


def save_index(index, meta):
    """Save FAISS index and metadata to disk."""
    paths = get_index_paths()
    os.makedirs(os.path.dirname(paths["index"]), exist_ok=True)
    
    faiss.write_index(index, paths["index"])
    with open(paths["meta"], "wb") as f:
        pickle.dump(meta, f)
    logger.info("Saved FAISS index and metadata")


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            return {"error": "Empty file"}

        # Check cache
        fh = file_hash(content)
        if is_cached(fh):
            return {"status": "already cached", "message": "File already uploaded"}
        
        # Use tempfile.NamedTemporaryFile for cross-platform compatibility
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Detect type and extract text
            if file.filename.endswith(".pdf"):
                text_data = pdf.load_pdf(tmp_path)
            elif file.filename.endswith(".docx"):
                text_data = docx.load_docx(tmp_path)
            elif file.filename.endswith(".pptx"):
                text_data = pptx.load_pptx(tmp_path)
            elif file.filename.endswith(".txt"):
                text_data = text.load_txt(tmp_path)
            elif file.filename.endswith(".json"):
                text_data = json_file.load_json(tmp_path)
            else:
                text_data = image_ocr.load_image(tmp_path)

            if not text_data or not text_data.strip():
                return {"error": "No text extracted"}

            chunks = chunk_text(text_data)
            if len(chunks) == 0:
                return {"error": "No chunks created"}

            logger.info("Processing file %s: extracted %d chunks", file.filename, len(chunks))

            # Embed chunks
            try:
                embeddings = embed(chunks)
                embeddings = np.array(embeddings, dtype=np.float32)
            except Exception as e:
                logger.exception("Failed to embed chunks")
                return {"error": f"Embedding failed: {e}"}

            # Load or create index
            try:
                index, meta = load_or_create_index()
            except Exception as e:
                logger.exception("Failed to load/create index")
                return {"error": f"Index load failed: {e}"}

            # Add to index
            try:
                index.add(embeddings)
                for chunk in chunks:
                    meta.append({"source": file.filename, "text": chunk})
                save_index(index, meta)
                add_cache(fh)
                logger.info("Added %d chunks to FAISS index; total docs now %d", len(chunks), len(meta))
            except Exception as e:
                logger.exception("Failed to add chunks to index")
                return {"error": f"Index update failed: {e}"}

            return {
                "status": "uploaded",
                "filename": file.filename,
                "chunks": len(chunks),
                "indexed": len(chunks),
                "total_docs": len(meta)
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    except Exception as e:
        logger.exception("Upload failed")
        return {"error": str(e)}
