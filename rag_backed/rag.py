import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env.local"
load_dotenv(ENV_PATH)

from groq import Groq

from retrieval import retrieve, enrich_temporal_query


def build_context(results):
    context_blocks = []

    for index, result in enumerate(results, start=1):
        block = (
            f"[Source {index}]\n"
            f"Chunk ID: {result['chunk_id']}\n"
            f"{result['content']}"
        )

        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def handle_simple_chat(query):
    """
    Handle messages that do not need retrieval.
    """

    normalized = query.strip().lower().rstrip("!?.")

    greetings = {
        "hi",
        "hello",
        "hey",
        "hi there",
        "hello there",
    }

    capability_questions = {
        "what can you do",
        "what can you help with",
        "how can you help",
        "what do you do",
        "help",
    }

    if normalized in greetings:
        return (
            "Hi! I can help you with the meal plan, "
            "cooking instructions, and shopping information."
        )

    if normalized in capability_questions:
        return (
            "I can help you with the website's meal plan, including "
            "what to eat today or tomorrow, cooking instructions, "
            "and shopping information."
        )

    return None


def generate_answer(query, context):
    """
    Generate an answer using ONLY retrieved website evidence.
    """

    client = Groq(
        api_key=os.environ["GROQ_API_KEY"]
    )

    system_prompt = """
You are the Food Planner website assistant.

Rules:
1. Answer only from the provided website context.
2. Do not use outside knowledge, infer missing facts, expand abbreviations,
   or add explanations that are not explicitly supported by the context.
3. If the context does not contain enough information, say exactly:
   "I couldn't find that information in this website's knowledge."
4. Ignore retrieved sources that are unrelated to the question.
5. Cite supporting evidence using exactly this format: [Source 1], [Source 2].
   Use normal square brackets only.
6. Keep the answer concise and useful.
7. Temporal context may be used only to understand words such as
   today, tonight, or tomorrow. Meal information must still come
   from the provided website context.
"""

    enriched_query = enrich_temporal_query(query)

    user_prompt = f"""
Question:
{enriched_query}

Website context:
{context}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        include_reasoning=False,
    )

    return response.choices[0].message.content


def answer_question(query):
    """
    Complete RAG pipeline for one user question.
    """

    simple_answer = handle_simple_chat(query)

    if simple_answer:
        return {
            "answer": simple_answer,
            "sources": [],
        }

    results = retrieve(query, top_k=3)

    context = build_context(results)

    answer = generate_answer(
        query,
        context,
    )

    sources = [
        {
            "chunk_id": result["chunk_id"],
            "metadata": result["metadata"],
            "similarity": result["similarity"],
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":
    questions = [
        "Hi",
        "What can you do?",
        "What's dinner tonight?",
    ]

    for question in questions:
        print("\nQUESTION:")
        print(question)

        result = answer_question(question)

        print("ANSWER:")
        print(result["answer"])

        print("SOURCES:")
        print(result["sources"])