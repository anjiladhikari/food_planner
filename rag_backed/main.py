from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    """
    Simple sanity check.

    Later the same API will expose our RAG chatbot,
    but for now we only prove that the backend works.
    """
    return {"status": "ok"}