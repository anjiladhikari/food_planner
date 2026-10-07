import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import answer_question
from vector_store import sync_index


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://anjiladhikari.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reindex")
def reindex(x_reindex_secret: str = Header(...)):
    """
    Refresh the public RAG index after the Google Sheet changes.
    """

    expected_secret = os.environ["REINDEX_SECRET"]

    if x_reindex_secret != expected_secret:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    sync_index()

    return {
        "status": "ok",
        "message": "RAG index synchronized",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    return answer_question(request.question)