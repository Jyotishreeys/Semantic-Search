from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.pdf_processor import process_pdf
from services.embeddings import get_embeddings
from services.vector_store import create_collection, store_embeddings, search_query
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

# Load .env variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="PDF Semantic Search API")

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure Qdrant collection exists at startup
create_collection()

# ---------- ROUTES ----------

@app.get("/")
def root():
    return {"message": "PDF Semantic Search API is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os

from services.pdf_processor import process_pdf
from services.embeddings import get_embeddings
from services.vector_store import store_embeddings, search_query, format_search_results_with_chunks

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Save uploaded PDF
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Process PDF: extract text, chunk, embed, store
    try:
        chunks_data = process_pdf(file_location)
        chunks_text = [c["chunk"] for c in chunks_data]
        embeddings = get_embeddings(chunks_text)
        store_embeddings(embeddings, chunks_data, pdf_name=file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Uploaded and processed {file.filename}", "total_chunks": len(chunks_data)}

# Model for search input
class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

@app.post("/search")
def search(req: SearchRequest):
    try:
        query_embedding = get_embeddings([req.query])[0]
        raw_results = search_query(query_embedding, top_k=req.top_k)
        
        # Format results for readability
        formatted_results = format_search_results_with_chunks(raw_results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"results": formatted_results}

