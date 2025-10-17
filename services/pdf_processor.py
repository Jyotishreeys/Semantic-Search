import os
from typing import List, Dict
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:  # avoid NoneType if page is empty
            text += page_text + "\n"
    
    return text

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Split text into chunks with optional overlap.
    Returns a list of dictionaries: {'chunk': text_chunk, 'start': start_index, 'end': end_index}
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end]
        chunks.append({
            'chunk': chunk_text,
            'start': start,
            'end': end
        })
        start += chunk_size - overlap  # move start by chunk_size minus overlap
    
    return chunks

def process_pdf(pdf_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Full PDF processing: extract text and split into chunks.
    """
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text_into_chunks(text, chunk_size, overlap)
    return chunks

if __name__ == "__main__":
    # Corrected path to uploads folder from project root
    test_pdf = "uploads/sample.pdf"  
    try:
        result = process_pdf(test_pdf)
        print(f"Total chunks: {len(result)}")
        if result:
            print(result[0])  # print first chunk
    except FileNotFoundError as e:
        print(e)
