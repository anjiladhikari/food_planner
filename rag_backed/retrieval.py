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
    queries = [
    # Should be answerable
    "How do I cook rolled oats?",
    "What is Day 2 lunch?",
    "Which rolled oats should I buy?",
    "How do I boil eggs?",

    # Should NOT be answerable
    "What is the weather today?",
    "Who is the prime minister of Australia?",
    "How do I install Docker?",
    "What is the capital of Japan?",
    ]

for query in queries:
    result = retrieve(query, top_k=1)[0]

    print(
        f"{result['similarity']:.4f} | "
        f"{query} | "
        f"{result['chunk_id']}"
    )