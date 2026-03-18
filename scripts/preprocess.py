import json
import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

def normalize_arabic(text):
    """
    Normalizes Arabic text for better search:
    - Removes Tashkeel (vowels).
    - Normalizes different forms of Alef (أ، إ، آ) to plain Alef (ا).
    - Normalizes Taa Marbuta (ة) to Haa (ه).
    - Normalizes Yaa (ى) to (ي).
    """
    # Remove Tashkeel (Fatha, Damma, Kasra, Shadda, etc.)
    tashkeel = re.compile(r'[\u064B-\u0652]')
    text = re.sub(tashkeel, "", text)
    
    # Simple Normalization
    text = re.sub(r'[أإآ]', 'ا', text)
    # text = re.sub(r'ة', 'ه', text)  # Optional, sometimes better to keep it
    # text = re.sub(r'ى', 'ي', text)  # Optional
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_chunks(input_path, output_path):
    """
    Loads extracted data, normalizes it, and splits it into semantic chunks.
    """
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Initialize Text Splitter
    # 600 chars is roughly 100-150 words, good for RAG.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    all_chunks = []

    print("🔄 Processing and Chunking...")
    for entry in data:
        original_text = entry["content"]
        # We normalize for indexing, but can keep original if needed.
        # For this stage, we'll normalize everything to ensure the LLM doesn't get confused.
        normalized_text = normalize_arabic(original_text)
        
        # Split text into chunks
        chunks = text_splitter.split_text(normalized_text)
        
        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "book": entry["book"],
                "page": entry["page"],
                "chunk_id": i + 1,
                "content": chunk_text
            })

    # Save processed chunks
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=4)

    print(f"✅ Created {len(all_chunks)} chunks from {len(data)} pages.")
    print(f"💾 Saved to {output_path}")

if __name__ == "__main__":
    INPUT_FILE = "data/processed/extracted_data.json"
    OUTPUT_FILE = "data/processed/chunks.json"
    create_chunks(INPUT_FILE, OUTPUT_FILE)
