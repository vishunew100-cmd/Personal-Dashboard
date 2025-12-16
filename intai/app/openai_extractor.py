import openai
import os
import json
import numpy as np

from app.embeddings import embed_chunks, embed_query

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a structured data extraction engine.

Multiple documents belong to the SAME person.

Rules:
- Merge data across documents
- Prefer repeated and consistent values
- Do NOT infer missing facts
- Output MUST strictly match the JSON schema
- Return ONLY valid JSON
"""

def retrieve_relevant_chunks(chunks: list[str], top_k: int = 8) -> list[str]:
    """
    Semantic retrieval using cosine similarity
    """
    chunk_embeddings = embed_chunks(chunks)
    query_embedding = embed_query(
        "Extract all personal, address, and credit-related information"
    )

    scores = chunk_embeddings @ query_embedding
    top_indices = np.argsort(scores)[-top_k:][::-1]

    return [chunks[i] for i in top_indices]


def extract_from_documents(chunks: list[str], schema: dict) -> dict:
    relevant_chunks = retrieve_relevant_chunks(chunks)

    context = "\n\n".join(
        f"--- DOCUMENT CHUNK {i+1} ---\n{chunk}"
        for i, chunk in enumerate(relevant_chunks)
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
DOCUMENT TEXT:
{context}

OUTPUT JSON SCHEMA:
{json.dumps(schema, indent=2)}

Instructions:
- Produce ONE unified JSON object
- Match schema exactly
"""
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": schema
        },
        max_tokens=3000
    )

    return json.loads(response["choices"][0]["message"]["content"])
