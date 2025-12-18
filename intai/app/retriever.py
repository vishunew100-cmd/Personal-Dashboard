import numpy as np
from app.embeddings import embed_chunks, embed_query

# Boost keywords strongly found in identity, addresses, jobs, credit reports
KEYWORDS = {
    "name": 1.8,
    "dob": 1.7,
    "birth": 1.6,
    "address": 1.9,
    "residence": 1.4,
    "ssn": 2.0,
    "social security": 2.0,
    "credit": 1.6,
    "account": 1.5,
    "balance": 1.3,
    "payment": 1.3,
    "employer": 1.4,
    "occupation": 1.4,
    "education": 1.3,
    "criminal": 1.7,
    "case": 1.5,
}

NOISE_PATTERNS = [
    "lorem", "ipsum",
    "intentionally left blank",
    "sample only",
    "page",
]


def keyword_score(chunk: str) -> float:
    text = chunk.lower()
    score = 0.0
    for word, weight in KEYWORDS.items():
        if word in text:
            score += weight
    return score


def noise_penalty(chunk: str) -> float:
    text = chunk.lower()
    penalty = 0.0
    for noise in NOISE_PATTERNS:
        if noise in text:
            penalty += 2.0
    return penalty


def hybrid_retrieve(chunks: list[str], top_k: int = 12) -> list[str]:
    """
    Hybrid retrieval combines:
    - semantic similarity
    - keyword boosting
    - noise penalty
    """

    # Semantic similarity embeddings
    embeddings = embed_chunks(chunks)
    query_emb = embed_query("Extract personal, address, family, jobs, identity, credit info")

    semantic_scores = embeddings @ query_emb

    final_scores = []
    for idx, chunk in enumerate(chunks):
        sem = semantic_scores[idx]
        key = keyword_score(chunk)
        noise = noise_penalty(chunk)
        final_scores.append(sem + key - noise)

    final_scores = np.array(final_scores)
    best_indices = np.argsort(final_scores)[-top_k:][::-1]

    return [chunks[i] for i in best_indices]
