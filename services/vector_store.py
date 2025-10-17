import os
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Configuration
# -----------------------------
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "pdf_documents")
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 embeddings have 384 dimensions

client = QdrantClient(url=QDRANT_URL)

# -----------------------------
# Collection Management
# -----------------------------
def create_collection():
    """
    Create Qdrant collection if it doesn't exist.
    """
    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print(f"Collection '{COLLECTION_NAME}' created.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

# -----------------------------
# Embedding Storage
# -----------------------------
def store_embeddings(embeddings: List[List[float]], chunks_data: List[Dict], pdf_name: str):
    """
    Store embeddings + metadata in Qdrant.
    """
    points = []
    for idx, (embedding, chunk) in enumerate(zip(embeddings, chunks_data)):
        points.append({
            "id": idx,
            "vector": embedding,
            "payload": {
                "pdf": pdf_name,
                "chunk_text": chunk["chunk"],
                "start": chunk["start"],
                "end": chunk["end"]
            }
        })
    
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"{len(points)} embeddings stored in collection '{COLLECTION_NAME}'.")

# -----------------------------
# Search
# -----------------------------
def search_query(query_embedding: List[float], top_k: int = 3) -> List[Dict]:
    """
    Search Qdrant for most similar chunks.
    """
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k
    )
    
    output = []
    for r in results:
        output.append({
            "id": r.id,
            "score": r.score,
            "pdf": r.payload.get("pdf"),
            "chunk_text": r.payload.get("chunk_text"),
            "start": r.payload.get("start"),
            "end": r.payload.get("end")
        })
    return output

# -----------------------------
# Formatting Results
# -----------------------------
def format_search_results_with_chunks(results: List[Dict]) -> List[Dict]:
    """
    Format raw search results to presentable sentences and also keep original chunk.
    """
    formatted = []
    for res in results:
        raw_chunk = res["chunk_text"]
        
        # Remove newlines and extra spaces
        text = ' '.join(raw_chunk.replace("\n", " ").split())
        
        formatted.append({
            "pdf": res["pdf"],
            "score": round(res["score"], 3),
            "text": text,               # nicely formatted sentence
            "original_chunk": raw_chunk  # raw chunk
        })
    return formatted

# -----------------------------
# Run as script for testing
# -----------------------------
if __name__ == "__main__":
    from pdf_processor import process_pdf
    from embeddings import get_embeddings

    pdf_path = "uploads/sample.pdf"
    chunks_data = process_pdf(pdf_path)
    chunks_text = [c["chunk"] for c in chunks_data]
    
    embeddings = get_embeddings(chunks_text)

    # Create collection and store
    create_collection()
    store_embeddings(embeddings, chunks_data, pdf_name="sample.pdf")

    # Test search with first embedding
    results = search_query(embeddings[0], top_k=2)
    formatted_results = format_search_results_with_chunks(results)

    print("Raw Results:", results)
    print("\nFormatted Results:", formatted_results)
