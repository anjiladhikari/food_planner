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
    Connect to hosted Supabase PostgreSQL.
    """
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SECRET_KEY"],
    )


def sync_index():
    """
    Synchronize current public Google Sheet knowledge
    with the pgvector RAG index.

    - New chunk      -> embed + insert
    - Changed chunk  -> re-embed + update
    - Unchanged      -> do nothing
    - Deleted chunk  -> remove from database
    """

    # 1. Build the current knowledge from Google Sheets.
    knowledge = load_public_knowledge()
    current_chunks = build_all_chunks(knowledge)

    supabase = get_supabase()

    # 2. Read what is already indexed.
    existing_rows = (
        supabase
        .table("rag_chunks")
        .select("id,text,metadata")
        .execute()
        .data
    )

    existing_by_id = {
        row["id"]: row
        for row in existing_rows
    }

    current_by_id = {
        chunk["id"]: chunk
        for chunk in current_chunks
    }

    # 3. Find new or changed chunks.
    changed_chunks = []

    for chunk_id, chunk in current_by_id.items():
        existing = existing_by_id.get(chunk_id)

        if (
            existing is None
            or existing["text"] != chunk["text"]
            or existing["metadata"] != chunk["metadata"]
        ):
            changed_chunks.append(chunk)

    # 4. Find chunks that no longer exist in Google Sheets.
    stale_ids = list(
        set(existing_by_id) - set(current_by_id)
    )

    # 5. Only call the embedding API when something changed.
    if changed_chunks:
        hf_client = get_client()
        embeddings = embed_documents(
            hf_client,
            changed_chunks,
        )

        rows = []

        for chunk, embedding in zip(
            changed_chunks,
            embeddings,
        ):
            rows.append(
                {
                    "id": chunk["id"],
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                    "embedding": embedding.tolist(),
                }
            )

        supabase.table("rag_chunks").upsert(rows).execute()

    # 6. Remove knowledge deleted from the source.
    if stale_ids:
        (
            supabase
            .table("rag_chunks")
            .delete()
            .in_("id", stale_ids)
            .execute()
        )

    print("Current chunks:", len(current_chunks))
    print("New/changed:", len(changed_chunks))
    print("Deleted:", len(stale_ids))


if __name__ == "__main__":
    sync_index()