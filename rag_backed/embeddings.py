import os

from huggingface_hub import InferenceClient

from ingest import load_public_knowledge
from chunks import build_all_chunks


MODEL_NAME = "BAAI/bge-small-en-v1.5"


def get_client():
    return InferenceClient(
        provider="hf-inference",
        api_key=os.environ["HF_TOKEN"],
    )


def embed_documents(client, chunks):
    """
    Input:
        Our 58 retrieval-ready chunks.

    Output:
        One 384-dimensional embedding for each chunk.
    """

    texts = [chunk["text"] for chunk in chunks]

    embeddings = client.feature_extraction(
        texts,
        model=MODEL_NAME,
    )

    return embeddings


if __name__ == "__main__":
    knowledge = load_public_knowledge()
    chunks = build_all_chunks(knowledge)

    client = get_client()
    embeddings = embed_documents(client, chunks)

    print("Chunks:", len(chunks))
    print("Embedding shape:", embeddings.shape)

    print("\nFirst chunk:")
    print(chunks[0]["id"])

    print("First vector shape:")
    print(embeddings[0].shape)