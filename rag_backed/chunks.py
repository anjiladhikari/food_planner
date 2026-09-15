import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from ingest import load_public_knowledge


def build_food_plan_chunks(food_plan):
    """
    Input:
        Normalized food-plan records.

    Output:
        Retrieval-ready chunks.

    Each meal/nutrition section becomes its own chunk
    so retrieval can return precise evidence.
    """

    chunks = []

    for record in food_plan:
        day = record["day"]

        sections = [
            "breakfast",
            "lunch",
            "dinner",
            "nutrition_cost",
        ]

        for section in sections:
            chunk = {
                "id": f"food_plan_{day.lower().replace(' ', '_')}_{section}",
                "text": (
                    f"Day: {day}\n"
                    f"Section: {section}\n"
                    f"{record[section]}"
                ),
                "metadata": {
                    "source_type": "food_plan",
                    "day": day,
                    "section": section,
                },
            }

            chunks.append(chunk)

    return chunks

def build_shopping_chunks(shopping):
    """
    Input:
        Normalized shopping records.

    Output:
        One retrieval-ready chunk per shopping item.
    """

    chunks = []

    for index, record in enumerate(shopping, start=1):
        chunk = {
            "id": f"shopping_{index}",
            "text": (
                f"Food item: {record['food_item']}\n"
                f"Recommended item: {record['recommended_item']}\n"
                f"Reason: {record['reason']}\n"
                f"Buying link: {record['buying_link']}"
            ),
            "metadata": {
                "source_type": "shopping",
                "food_item": record["food_item"],
            },
        }

        chunks.append(chunk)

    return chunks


def build_cooking_chunks(cooking):
    """
    Input:
        Normalized cooking records.

    Output:
        One retrieval-ready chunk per cooking item.
    """

    chunks = []

    for index, record in enumerate(cooking, start=1):
        chunk = {
            "id": f"cooking_{index}",
            "text": (
                f"Food item: {record['food_item']}\n"
                f"Equipment: {record['equipment']}\n"
                f"Method: {record['method']}\n"
                f"Pro tip: {record['pro_tip']}"
            ),
            "metadata": {
                "source_type": "cooking",
                "food_item": record["food_item"],
            },
        }

        chunks.append(chunk)

    return chunks


def build_all_chunks(knowledge):
    """
    Input:
        Knowledge dict from load_public_knowledge().

    Output:
        Single list of all retrieval-ready chunks.
    """

    food_plan_chunks=build_food_plan_chunks(
        knowledge["food_plan"]
    )
    shopping_chunks=build_shopping_chunks(
        knowledge["shopping"]
    )
    cooking_chunks=build_cooking_chunks(
        knowledge["cooking"]
    )



    return  food_plan_chunks+shopping_chunks+cooking_chunks
    


if __name__ == "__main__":
    knowledge = load_public_knowledge()

    chunks = build_all_chunks(knowledge)

    print("Total chunks:", len(chunks))

    print("\nCounts by source:")
    print(
        "Food plan:",
        sum(
            1 for chunk in chunks
            if chunk["metadata"]["source_type"] == "food_plan"
        )
    )

    print(
        "Shopping:",
        sum(
            1 for chunk in chunks
            if chunk["metadata"]["source_type"] == "shopping"
        )
    )

    print(
        "Cooking:",
        sum(
            1 for chunk in chunks
            if chunk["metadata"]["source_type"] == "cooking"
        )
    )

