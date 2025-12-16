import openai
import os
import numpy as np

openai.api_key = os.getenv("OPENAI_API_KEY")

EMBED_MODEL = "text-embedding-3-small"

def embed_chunks(chunks: list[str]) -> np.ndarray:
    """
    Returns normalized embeddings matrix (N x D)
    """
    response = openai.Embedding.create(
        model=EMBED_MODEL,
        input=chunks
    )

    embeddings = np.array([d["embedding"] for d in response["data"]])
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norms


def embed_query(query: str) -> np.ndarray:
    response = openai.Embedding.create(
        model=EMBED_MODEL,
        input=query
    )
    emb = np.array(response["data"][0]["embedding"])
    return emb / np.linalg.norm(emb)
