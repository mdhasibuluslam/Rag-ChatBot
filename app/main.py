from fastapi import FastAPI
from pydantic import BaseModel
from rag_engine import rag_answer

app = FastAPI()

class Query(BaseModel):
    query: str


@app.get('/')
def show():
    return {
        'massege': 'Hello Bro'
    }


@app.post("/chat")
async def chat(data: Query):
    return rag_answer(data.query)
