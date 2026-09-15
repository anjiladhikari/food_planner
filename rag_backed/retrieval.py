from vector_store import get_supabase
from embeddings import get_client, embed_query


def retrieve(query, top_k=5):
    """
    Input:
        Natural-language user query.

    Output:
        Top-K chunks ranked by cosine similarity.
    """

    # 1. Convert the question into a vector
    hf_client = get_client()
    query_embedding = embed_query(hf_client, query)

    # 2. Ask PostgreSQL/pgvector to compare it
    #    against our 58 stored document vectors.
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
    query = "How do I cook rolled oats?"

    results = retrieve(query, top_k=5)

    print(f"\nQuery: {query}\n")

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. {result['chunk_id']} "
            f"(similarity={result['similarity']:.4f})"
        )
        print(result["content"])
        print()