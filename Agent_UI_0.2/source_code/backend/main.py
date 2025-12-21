from fastapi import FastAPI
from api.chat import router as chat_router
from api.upload import router as upload_router

app = FastAPI()
app.include_router(chat_router)
app.include_router(upload_router)

@app.get("/")
def health():
    return {"status": "ok"}


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
