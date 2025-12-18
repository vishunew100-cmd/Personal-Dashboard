import json
import os
import re
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You extract structured information from documents.

Rules:
- Use ONLY facts present in the text.
- Do NOT guess or hallucinate.
- If a field is missing, return:
  - "" for strings
  - [] for arrays
  - 0 for numbers
- Return EXACTLY the JSON schema structure provided.
- Output ONLY valid JSON.
- Do NOT wrap JSON in markdown.
"""


def _clean_json(text: str) -> str:
    """Remove ```json fences if model adds them"""
    text = text.strip()
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()

def extract_from_documents(chunks: list[str], schema: dict) -> dict:
    """
    SIMPLE, RELIABLE extractor:
    - Sends ALL text to model
    - No tools
    - No retrieval
    - Saves output JSON named after person
    """

    full_text = "\n\n".join(chunks)

    user_prompt = f"""
DOCUMENT TEXT:
--------------------
{full_text}
--------------------

Extract structured data using EXACTLY this schema:

{json.dumps(schema, indent=2)}

STRICT:
- Output ONLY valid JSON
- No markdown
- No explanation
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        temperature=0,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=5000,
    )

    raw_text = response.output_text
    cleaned = _clean_json(raw_text)

    try:
        parsed = json.loads(cleaned)
    except Exception as e:
        return {
            "error": "Model returned invalid JSON",
            "exception": str(e),
            "model_output": raw_text,
        }

    return parsed
