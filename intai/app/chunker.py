import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def chunk_text(text: str, max_tokens=800, overlap=100):
    words = text.split()
    chunks, start = [], 0

    while start < len(words):
        end = start + max_tokens
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max_tokens - overlap
    return chunks
