from vector_store import get_supabase
from embeddings import get_client, embed_query


def retrieve(query, top_k=5):
    """
    Embed a user query and retrieve the Top-K
    most similar chunks from pgvector.
    """

    # Query -> 384-dimensional embedding
    hf_client = get_client()
    query_embedding = embed_query(hf_client, query)

    # Vector similarity search in PostgreSQL
    supabase = get_supabase()

    result = supabase.rpc(
        "match_rag_chunks",
        {
            "query_embedding": query_embedding.tolist(),
            "match_count": top_k,
        },
    ).execute()

    return result.data


if __name__ == "__main__":
    # Optional manual retrieval test.
    # This will NOT run when rag.py imports retrieve().
    query = "How do I cook rolled oats?"

    results = retrieve(query, top_k=3)

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. {result['chunk_id']} "
            f"(similarity={result['similarity']:.4f})"
        )
        print(result["content"])
        print()