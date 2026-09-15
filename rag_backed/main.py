from fastapi import FastAPI
from pydantic import BaseModel

from rag import answer_question

from fastapi.middleware.cors import CORSMiddleware
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


@app.post("/chat")
def chat(request: ChatRequest):
    """
    Input:
        {
            "question": "How do I cook rolled oats?"
        }

    Output:
        {
            "answer": "...",
            "sources": [...]
        }
    """
    return answer_question(request.question)