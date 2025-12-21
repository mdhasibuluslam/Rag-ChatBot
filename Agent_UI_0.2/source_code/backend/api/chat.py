from fastapi import APIRouter
from vectorstore.faiss_store import FaissStore
from vectorstore.embedder import embed
from llm.generate import generate_answer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
store = FaissStore()

from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
def chat(req: ChatRequest):
    query = req.query

    logger.info("/chat received query: %s", query)

    try:
        docs = store.search(query, top_k=5)
    except Exception as e:
        logger.exception("Faiss search failed")
        return {"answer": f"Search error: {e}"}

    if not docs:
        logger.info("No docs found for query: %s; falling back to model-only generation", query)
        try:
            answer = generate_answer(question=query, context="")
            return {"answer": answer}
        except Exception as e:
            logger.exception("Model fallback failed")
            return {"answer": "I couldn't find relevant content, and model fallback failed."}

    # build context from returned docs
    try:
        context = "\n".join([d.get("text", "") for d in docs if d.get("text")])
    except Exception:
        context = ""

    logger.info("Found %d docs; context length=%d", len(docs), len(context))

    try:
        answer = generate_answer(
            question=query,
            context=context
        )
    except Exception as e:
        logger.exception("generate_answer failed")
        return {"answer": f"Model error: {e}"}

    return {"answer": answer}




