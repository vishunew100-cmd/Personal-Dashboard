import os
import numpy as np
from openai import OpenAI

# Load OpenAI client (reads OPENAI_API_KEY automatically)
client = OpenAI()

EMBED_MODEL = "text-embedding-3-small"


def embed_chunks(chunks: list[str]) -> np.ndarray:
    """
    Returns normalized embeddings matrix (N x D)
    """
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=chunks
    )

    # Extract embeddings
    embeddings = np.array([item.embedding for item in response.data])

    # Normalize rowwise
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms


def embed_query(query: str) -> np.ndarray:
    """
    Returns normalized embedding vector for a query
    """
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=query
    )

    emb = np.array(response.data[0].embedding)
    return emb / np.linalg.norm(emb)
