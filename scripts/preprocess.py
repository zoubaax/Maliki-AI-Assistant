import json
import os
import re
import unicodedata
from langchain_text_splitters import RecursiveCharacterTextSplitter


def is_reversed_arabic(text):
    """
    Heuristic to check if Arabic text is reversed by looking for common markers
    that appear in their visual (reversed) forms.
    """
    # These are common words or particles in their visually REVERSED forms
    # Example: 'على' -> 'ىلع', 'في' -> 'ىف', 'من' -> 'نم'.
    reversed_markers = [
        'هللا',   # الله
        'دمحم',   # محمد
        'ىلا',    # الى
        'ىلع',    # على
        'ىف',     # فى
        'هذهف',   # هذه
        'نم',     # من
        'نع',     # عن
        'يتلا',   # التي
        'نايب',   # بيان
        'هبهذم',  # مذهبه
        'هباحصأ', # أصحابه
        'نيدلا',  # الدين
        'هقفلا',  # الفقه
        'بولملا'  # المطلوب
    ]
    # If we find at least 2 markers, or 1 strong marker in a short text
    count = sum(1 for marker in reversed_markers if marker in text)
    
    # Check for reversed particles/common words which are hard to miss if the whole text is reversed
    if count >= 1:
        # Check if the word order also looks reversed?
        # Actually, visual OCR often reverses the whole line character-by-character.
        return True
    return False

def fix_visual_arabic(text):
    """
    Fixes reversed Arabic text and swaps brackets.
    """
    if not is_reversed_arabic(text):
        return text
    
    # Reverse the whole string
    text = text[::-1]
    
    # Swap parentheses and brackets because they get flipped in character reversal
    swaps = str.maketrans("()[]<>{}", ")(][><}{")
    text = text.translate(swaps)
    return text

def normalize_arabic(text):
    """
    Normalizes Arabic text and cleans garbage OCR artifacts.
    """
    # 0. Standardize character forms (converts visual presentation forms to logical)
    text = unicodedata.normalize('NFKC', text)
    
    # 1. Preliminary cleanup of non-Arabic filler noise often at ends or in headers

    # Remove strings of non-Arabic letters/numbers that look like noise
    text = re.sub(r'[A-Za-z0-9]{5,}', ' ', text) # Remove long latin sequences
    
    # 2. Fix Visual Reversal (if detected)
    text = fix_visual_arabic(text)
    
    # 3. Clean up generic noise
    text = re.sub(r'[A-Z]{2,}', ' ', text) # Remove uppercase sequences (like HE, HH, BR)
    text = re.sub(r'[\u0000-\u001F\u007F-\u009F]', ' ', text) # Remove non-printable
    
    # 4. Remove Tashkeel (vowels) except for essential ones if needed (usually removed for RAG)
    tashkeel = re.compile(r'[\u064B-\u0652]')
    text = re.sub(tashkeel, "", text)
    
    # 5. Arabic character normalization
    text = re.sub(r'[أإآ]', 'ا', text)
    # We keep 'ى' vs 'ي' as some users prefer original spelling, 
    # but the LLM is usually fine with either.
    
    # 6. Remove OCR artifacts like multiple symbols or dots
    text = re.sub(r'[ـ]{1,}', '', text) # Remove kashida (stretching character)
    
    # 7. Keep basic punctuation but remove other noise
    # We allow Arabic letters, English letters (for citations/names), numbers, and basic punctuation
    text = re.sub(r'[^\w\s\u0600-\u06FF\.\,\?\!\(\)\[\]]', ' ', text)
    
    # 8. Final cleanup of multiple spaces
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
        normalized_text = normalize_arabic(original_text)
        
        # Filter out pages that are too short or mostly garbage after normalization
        if len(normalized_text) < 10:
            continue
            
        # Optional: Check Arabic character density
        # Include standard Arabic, supplements, and presentation forms A & B
        # Standard: \u0600-\u06FF
        # Extended/Supp: \u0750-\u077F, \u08A0-\u08FF
        # Presentation Forms: \uFB50-\uFDFF, \uFE70-\uFEFF
        arabic_range = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        arabic_chars = len(arabic_range.findall(normalized_text))
        
        if len(normalized_text) > 0 and (arabic_chars / len(normalized_text)) < 0.3:
            # Lowering the threshold slightly as some OCR has more noise 
            # and ensuring we catch the Presentation Forms.
            continue


        # Split text into chunks
        chunks = text_splitter.split_text(normalized_text)
        
        for i, chunk_text in enumerate(chunks):
            # Final check on chunk quality
            if len(chunk_text) < 20:
                continue
            
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
