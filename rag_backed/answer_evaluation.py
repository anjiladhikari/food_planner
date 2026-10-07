from rag import answer_question


TEST_CASES = [
    {
        "query": "How do I cook rolled oats?",
        "type": "answerable",
        "expected_source": "cooking_1",
    },
    {
        "query": "Which rolled oats should I buy?",
        "type": "answerable",
        "expected_source": "shopping_1",
    },
    {
        "query": "What is Day 2 lunch?",
        "type": "answerable",
        "expected_source": "food_plan_day_2_lunch",
    },
    {
        "query": "How do I boil eggs?",
        "type": "answerable",
        "expected_source": "cooking_2",
    },
    {
        "query": "What is the weather today?",
        "type": "unanswerable",
        "expected_source": None,
    },
    {
        "query": "What is the capital of Japan?",
        "type": "unanswerable",
        "expected_source": None,
    },
]


if __name__ == "__main__":
    for index, case in enumerate(TEST_CASES, start=1):
        result = answer_question(case["query"])

        print("\n" + "=" * 60)
        print(f"TEST {index}")
        print("Query:", case["query"])
        print("Type:", case["type"])
        print("Expected source:", case["expected_source"])

        print("\nAnswer:")
        print(result["answer"])

        print("\nRetrieved sources:")
        for source in result["sources"]:
            print(
                source["chunk_id"],
                round(source["similarity"], 4),
            )