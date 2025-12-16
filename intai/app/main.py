from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from typing import List

from app.pdf_reader import extract_text_from_pdf
from app.chunker import chunk_text
from app.openai_extractor import extract_from_documents
from app.schema_loader import load_output_schema

app = FastAPI(title="Multi-PDF Person Data Extractor")

OUTPUT_SCHEMA = load_output_schema()


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Multi-PDF Person Data Extractor"
    }



@app.post("/extract")
async def extract_person_data(
    files: List[UploadFile] = File(...)
):
    all_chunks = []

    for pdf in files:
        pdf_bytes = await pdf.read()
        text = extract_text_from_pdf(pdf_bytes)
        chunks = chunk_text(text)
        all_chunks.extend(chunks)

    extracted_data = extract_from_documents(
        chunks=all_chunks,
        schema=OUTPUT_SCHEMA
    )

    return {
        "data": extracted_data
    }
