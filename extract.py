import fitz  # PyMuPDF
import json
import os
import re

def clean_text(text):
    """
    Cleans extracted Arabic text:
    - Normalizes multiple spaces into a single space.
    - Removes unnecessary lines with only punctuation.
    - Fixes common encoding issues or artifacts.
    """
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_pdf_pages(pdf_path):
    """
    Extracts text page-by-page from a PDF file.
    """
    print(f"📖 Reading: {os.path.basename(pdf_path)}")
    doc = fitz.open(pdf_path)
    book_title = os.path.basename(pdf_path).replace(".pdf", "")
    
    pages_data = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        
        # We might need to handle RTL ordering if it's messed up,
        # but fitz is usually good for digital PDFs.
        cleaned_text = clean_text(text)
        
        if cleaned_text:
            pages_data.append({
                "book": book_title,
                "page": page_num + 1,  # human-readable page 1
                "content": cleaned_text
            })
            
    print(f"✅ Extracted {len(pages_data)} pages from {book_title}.")
    return pages_data

def save_manifest(data, output_path="data/processed/extracted_data.json"):
    """
    Saves extracted text to a JSON file for later chunking.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"💾 Data saved to {output_path}")

if __name__ == "__main__":
    # Point to your book folder or a specific file
    BOOK_PATH = "books/كتاب  مختصر عبد الرحمن الأخضري في العبادات على مذهب الإمام مالك.pdf"
    
    if os.path.exists(BOOK_PATH):
        extracted_data = extract_pdf_pages(BOOK_PATH)
        save_manifest(extracted_data)
    else:
        print(f"❌ File not found at {BOOK_PATH}. Please check the filename.")
