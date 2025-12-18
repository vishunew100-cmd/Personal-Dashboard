from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi import HTTPException, Query
from typing import List
import json
import os
import re
from app.pdf_reader import extract_text_from_pdf
from app.chunker import chunk_text
from app.openai_extractor import extract_from_documents
from app.schema_loader import load_output_schema
from app.validator import validate_extracted_profile

app = FastAPI(title="Multi-PDF Person Data Extractor")

OUTPUT_SCHEMA = load_output_schema()
OUTPUT_DIR = "output"

def _safe_filename(name: str) -> str:
    """
    Convert name to filesystem-safe filename
    """
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Multi-PDF Person Data Extractor"
    }

@app.post("/extract")
async def extract_person_data(files: List[UploadFile] = File(...)):
    all_chunks = []

    for pdf in files:
        pdf_bytes = await pdf.read()

        text = extract_text_from_pdf(pdf_bytes)
        chunks = chunk_text(text)

        print(f"PDF '{pdf.filename}' → {len(chunks)} chunks")

        all_chunks.extend(chunks)

    print("Total chunks sent to extractor:", len(all_chunks))

    extracted_data = extract_from_documents(
        chunks=all_chunks,
        schema=OUTPUT_SCHEMA
    )

    validated_data = validate_extracted_profile(extracted_data)

     # ---- Determine filename from identity.name ----
    person_name = validated_data.get("identity", {}).get("name", "")
    if person_name:
        filename = _safe_filename(person_name) + ".json"
    else:
        filename = "unknown_person.json"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(validated_data, f, indent=2)

    return {"data": validated_data}

@app.get("/profile")
def get_profile(name: str = Query(..., description="Person name")):
    """
    Fetch extracted profile JSON by person name.
    """

    safe_name = _safe_filename(name)
    filename = f"{safe_name}.json"
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"No profile found for name: {name}"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read profile file: {str(e)}"
        )

    return {
        "status": "ok",
        "filename": filename,
        "data": data
    }

@app.get("/profiles")
def list_profiles():
    if not os.path.exists(OUTPUT_DIR):
        return {"profiles": []}

    files = [
        f.replace(".json", "")
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith(".json")
    ]

    return {
        "count": len(files),
        "profiles": files
    }
