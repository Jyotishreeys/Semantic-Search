from typing import List
from sentence_transformers import SentenceTransformer
# Load the model (you can change model name in .env later)
model = SentenceTransformer("all-MiniLM-L6-v2")
def get_embeddings(chunks: List[str]) -> List[List[float]]:
    """
    Convert a list of text chunks into embeddings (vectors).
    """
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings
if __name__ == "__main__":
    from pdf_processor import process_pdf

    # Process sample PDF
    test_pdf = "uploads/sample.pdf"
    chunks_data = process_pdf(test_pdf)
    
    # Extract only text for embeddings
    chunks_text = [c['chunk'] for c in chunks_data]

    embeddings = get_embeddings(chunks_text)
    print(f"Total embeddings: {len(embeddings)}")
    print(f"First embedding vector (truncated): {embeddings[0][:10]}")  # print first 10 numbers
