import os
from pathlib import Path

from dotenv import load_dotenv
ENV_PATH = Path(__file__).resolve().parent.parent / ".env.local"
load_dotenv(ENV_PATH)

from groq import Groq

from retrieval import retrieve


ENV_PATH = Path(__file__).resolve().parent.parent / ".env.local"
load_dotenv(ENV_PATH)


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
2. Do not use outside knowledge.
3. If the context does not contain enough information, say:
   "I couldn't find that information in this website's knowledge."
4. Ignore retrieved sources that are unrelated to the question.
5. Cite supporting evidence using [Source 1], [Source 2], etc.
6. Keep the answer concise and useful.
"""

    user_prompt = f"""
Question:
{query}

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

    Input:
        Natural-language question.

    Output:
        Answer plus the retrieved source information.
    """

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
    result = answer_question(
        "How do I cook rolled oats?"
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(source)