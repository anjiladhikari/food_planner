from fastapi import FastAPI
from pydantic import BaseModel

from rag import answer_question


app = FastAPI()


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