from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from vector_store import get_supabase
from embeddings import get_client, embed_query


APP_TIMEZONE = ZoneInfo("Australia/Melbourne")


def enrich_temporal_query(query):
    """
    Add current weekday information only when the
    user asks using relative time words.

    Examples:
        "dinner tonight"
        -> "dinner tonight\nToday is Wednesday."

        "breakfast tomorrow"
        -> "breakfast tomorrow\nTomorrow is Thursday."
    """

    query_lower = query.lower()
    now = datetime.now(APP_TIMEZONE)

    temporal_context = []

    if "today" in query_lower or "tonight" in query_lower:
        temporal_context.append(
            f"Today is {now.strftime('%A')}."
        )

    if "tomorrow" in query_lower:
        tomorrow = now + timedelta(days=1)

        temporal_context.append(
            f"Tomorrow is {tomorrow.strftime('%A')}."
        )

    if not temporal_context:
        return query

    return (
        query
        + "\nTemporal context: "
        + " ".join(temporal_context)
    )


def retrieve(query, top_k=5):
    """
    Embed a user query and retrieve the Top-K
    most similar chunks from pgvector.
    """

    search_query = enrich_temporal_query(query)

    # Query -> 384-dimensional embedding
    hf_client = get_client()
    query_embedding = embed_query(
        hf_client,
        search_query,
    )

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
    query = "What's dinner tonight?"

    print("Original query:")
    print(query)

    print("\nRetrieval query:")
    print(enrich_temporal_query(query))

    print("\nResults:")

    results = retrieve(query, top_k=3)

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. {result['chunk_id']} "
            f"(similarity={result['similarity']:.4f})"
        )

        print(result["content"])
        print()