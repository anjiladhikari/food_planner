import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

from ingest import load_public_knowledge
from chunks import build_all_chunks
from embeddings import get_client, embed_documents



ENV_PATH = Path(__file__).resolve().parent.parent / ".env.local"
load_dotenv(ENV_PATH)


def get_supabase():
    """
    Connect to our hosted Supabase PostgreSQL database.
    """
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SECRET_KEY"],
    )


if __name__ == "__main__":
    # 1. Load public knowledge
    knowledge = load_public_knowledge()

    # 2. Build all 58 chunks
    chunks = build_all_chunks(knowledge)

    # 3. Create embeddings for all chunks
    hf_client = get_client()
    embeddings = embed_documents(hf_client, chunks)

    print("Chunks:", len(chunks))
    print("Embeddings:", embeddings.shape)

    # 4. Prepare rows for Supabase
    rows = []

    for chunk, embedding in zip(chunks, embeddings):
        rows.append(
            {
                "id": chunk["id"],
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "embedding": embedding.tolist(),
            }
        )

    # 5. Store everything
    supabase = get_supabase()

    supabase.table("rag_chunks").upsert(rows).execute()

    print(f"Indexed {len(rows)} chunks successfully")




