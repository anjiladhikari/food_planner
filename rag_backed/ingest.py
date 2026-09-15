import json
import requests


SHEET_ID = "1QwwTSwh7imbzvkHXPvvtZ5awNyf41r_aMnQUsLFivAY"


def fetch_sheet(sheet_name: str):
    """
    Input:
        Google Sheet tab name, e.g. "food plan"

    Output:
        Raw rows as Python lists.

    At this stage we are NOT cleaning or chunking anything.
    """

    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq"

    response = requests.get(
        url,
        params={
            "tqx": "out:json",
            "sheet": sheet_name,
        },
        timeout=20,
    )

    response.raise_for_status()

    # Google wraps the JSON inside JavaScript text.
    # Instead of assuming an exact character position,
    # extract the JSON object between the first { and last }.
    text = response.text
    json_text = text[text.find("{"): text.rfind("}") + 1]

    data = json.loads(json_text)

    rows = []

    for row in data["table"]["rows"]:
        values = [
            cell.get("v", "") if cell else ""
            for cell in row["c"]
        ]
        rows.append(values)

    return rows

def normalize_food_plan(rows):
    """
    Input:
        Raw Google Sheet rows including the header.

    Output:
        Structured food-plan records with named fields.
    """

    # First row contains column names, not actual meal data.
    data_rows = rows[1:]

    documents = []

    for row in data_rows:
        document = {
            "day": row[0],
            "breakfast": row[1],
            "lunch": row[2],
            "dinner": row[3],
            "nutrition_cost": row[4],
        }

        documents.append(document)

    return documents


def normalize_shopping(rows):
    """
    Input:
        Raw rows from "cooking links and which food"

    Output:
        Structured shopping records
    """

    data_rows = rows[1:]

    documents = []

    for row in data_rows:
        document = {
            "food_item": row[0],
            "recommended_item": row[1],
            "reason": row[2],
            "buying_link": row[3],
        }

        documents.append(document)

    return documents


def normalize_cooking(rows):
    """
    Input:
        Raw rows from "how to cook"

    Output:
        Structured cooking records
    """

    data_rows = rows[1:]

    documents = []

    for row in data_rows:
        document = {
            "food_item": row[0],
            "equipment": row[1],
            "method": row[2],
            "pro_tip": row[3],
        }

        documents.append(document)

    return documents

def validate_sheet(rows, expected_header, source_name):
    """
    Fail early if a Google Sheet no longer has the schema we expect.
    """
    if not rows:
        raise ValueError(f"{source_name}: sheet is empty")

    actual_header = rows[0]

    if actual_header != expected_header:
        raise ValueError(
            f"{source_name}: unexpected columns\n"
            f"Expected: {expected_header}\n"
            f"Actual:   {actual_header}"
        )


def load_public_knowledge():
    food_plan_rows = fetch_sheet("food plan")
    shopping_rows = fetch_sheet("cooking links and which food")
    cooking_rows = fetch_sheet("how to cook")

    validate_sheet(
        food_plan_rows,
        [
            "Day",
            "Breakfast (8–9 AM)",
            "Lunch (1–3 PM)",
            "Dinner (6–7 PM)",
            "Approx. Daily Nutrition & Cost",
        ],
        "food plan",
    )

    validate_sheet(
        shopping_rows,
        [
            "Food Item",
            "Recommended Brand / Type",
            "Why It's 100% Clean",
            "Buying Link",
        ],
        "shopping",
    )

    validate_sheet(
        cooking_rows,
        [
            "Food Item",
            "Primary Equipment",
            "Simplest Method",
            "Pro-Tip for Best Results",
        ],
        "cooking",
    )

    return {
        "food_plan": normalize_food_plan(food_plan_rows),
        "shopping": normalize_shopping(shopping_rows),
        "cooking": normalize_cooking(cooking_rows),
    }

if __name__ == "__main__":
    knowledge = load_public_knowledge()

    print("Food plan:", len(knowledge["food_plan"]))
    print("Shopping:", len(knowledge["shopping"]))
    print("Cooking:", len(knowledge["cooking"]))