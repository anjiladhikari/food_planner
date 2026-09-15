from retrieval import retrieve








TEST_CASES = [
    {
        "query": "How do I cook rolled oats?",
        "relevant_ids": ["cooking_1"],
    },
    {
        "query": "Which rolled oats should I buy?",
        "relevant_ids": ["shopping_1"],
    },
    {
        "query": "What is Day 1 breakfast?",
        "relevant_ids": ["food_plan_day_1_breakfast"],
    },
    {
        "query": "What do I eat for lunch on Day 2?",
        "relevant_ids": ["food_plan_day_2_lunch"],
    },
    {
        "query": "How do I boil eggs?",
        "relevant_ids": ["cooking_2"],
    },
    {
        "query": "How should I cook potatoes?",
        "relevant_ids": ["cooking_8"],
    },
    {
        "query": "Which rolled oats should I buy and how do I cook them?",
        "relevant_ids": [
            "shopping_1",
            "cooking_1",
        ],
    },
]
def recall_at_k(retrieved_ids, relevant_ids):
    relevant = set(relevant_ids)

    found = sum(
        1 for chunk_id in relevant
        if chunk_id in retrieved_ids
    )

    return found / len(relevant)


def precision_at_k(retrieved_ids, relevant_ids):
    relevant = set(relevant_ids)

    relevant_retrieved = sum(
        1 for chunk_id in retrieved_ids
        if chunk_id in relevant
    )

    return relevant_retrieved / len(retrieved_ids)


def reciprocal_rank(retrieved_ids, relevant_ids):
    relevant = set(relevant_ids)

    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant:
            return 1 / rank

    return 0.0


if __name__ == "__main__":
    k = 3

    all_recall = []
    all_precision = []
    all_hit = []
    all_rr = []

    for case in TEST_CASES:
        query = case["query"]
        relevant_ids = case["relevant_ids"]

        # Retrieve only once per query.
        results = retrieve(query, top_k=k)

        retrieved_ids = [
            result["chunk_id"]
            for result in results
        ]

        recall = recall_at_k(
            retrieved_ids,
            relevant_ids,
        )

        precision = precision_at_k(
            retrieved_ids,
            relevant_ids,
        )

        hit = int(
            any(
                chunk_id in set(relevant_ids)
                for chunk_id in retrieved_ids
            )
        )

        rr = reciprocal_rank(
            retrieved_ids,
            relevant_ids,
        )

        all_recall.append(recall)
        all_precision.append(precision)
        all_hit.append(hit)
        all_rr.append(rr)

        print(f"\nQuery: {query}")
        print("Retrieved:", retrieved_ids)
        print(f"Recall@{k}:    {recall:.2f}")
        print(f"Precision@{k}: {precision:.2f}")
        print(f"Hit@{k}:       {hit}")
        print(f"Reciprocal:  {rr:.2f}")

    print("\n===== BASELINE =====")
    print(f"Recall@{k}:    {sum(all_recall) / len(all_recall):.2f}")
    print(f"Precision@{k}: {sum(all_precision) / len(all_precision):.2f}")
    print(f"Hit@{k}:       {sum(all_hit) / len(all_hit):.2f}")
    print(f"MRR:         {sum(all_rr) / len(all_rr):.2f}")


