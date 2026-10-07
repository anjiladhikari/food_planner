import os

from fastapi import FastAPI, Header, HTTPException
from vector_store import sync_index
app = FastAPI()


@app.get("/health")
def health():
    """
    Simple sanity check.

    Later the same API will expose our RAG chatbot,
    but for now we only prove that the backend works.
    """
    return {"status": "ok"}

@app.post("/reindex")
def reindex(x_reindex_secret: str = Header(...)):
    """
    Refresh the public RAG index.

    This endpoint will later be called automatically
    when the Google Sheet changes.
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