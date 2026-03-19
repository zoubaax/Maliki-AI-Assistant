# 🔬 Technical Deep Dive: The Maliki AI Data Pipeline

This document explains the full technical pipeline used to transform raw Arabic PDF books into a searchable, AI-powered knowledge base.

---

## 📊 Pipeline Overview

```
📚 Raw PDF Books
      │
      ▼
┌─────────────────────┐
│  1. EXTRACTION      │  PyMuPDF (fitz) — Page-by-page text extraction
│  scripts/extract.py │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. PREPROCESSING   │  Arabic NLP — Normalization, RTL fixing, chunking
│  scripts/preprocess │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. EMBEDDING       │  Sentence Transformers — Convert text → 384-dim vectors
│  scripts/ingest.py  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. VECTOR STORE    │  PostgreSQL + pgvector — Store and query embeddings
│  Neon Cloud DB      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. RAG RETRIEVAL   │  Cosine Distance Search → Top-K relevant chunks
│  app/main.py        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  6. LLM GENERATION  │  Google Gemini 2.5 Flash → Scholarly Arabic answer
│  app/main.py        │
└─────────────────────┘
```

---

## 🔍 Stage 1: PDF Text Extraction

**File**: `scripts/extract.py`  
**Library**: [PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/)

### How it works:
PyMuPDF is used because it handles **digital Arabic PDFs** better than OCR-based tools. For each book, it reads the PDF page-by-page and extracts the raw text.

```python
doc = fitz.open(pdf_path)
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text = page.get_text("text")
```

### Key decisions:
- **Page-level extraction**: Each page is stored as a separate record with its `page_number` and `book_title`. This is what powers the **"Source: [Book, Page X]"** citations in answers.
- **`get_text("text")` mode**: This extracts the logical Unicode text, which is essential for Arabic RTL (Right-to-Left) scripts.
- **Initial cleaning**: A `clean_text()` function collapses multiple whitespace characters into a single space using `re.sub(r'\s+', ' ', text)`.

### Output:
```json
[
  { "book": "المدونة الكبرى", "page": 1, "content": "بسم الله الرحمن الرحيم..." },
  { "book": "المدونة الكبرى", "page": 2, "content": "..." }
]
```

---

## 🧹 Stage 2: Arabic Text Preprocessing

**File**: `scripts/preprocess.py`  
**Libraries**: `unicodedata`, `re`, `langchain_text_splitters`

This is the most technically complex stage. Raw Arabic PDF text often contains significant noise that must be cleaned before it can be meaningfully embedded.

### 2a. Unicode Normalization
```python
text = unicodedata.normalize('NFKC', text)
```
**NFKC** (Compatibility Decomposition, followed by Canonical Composition) standardizes characters. For example, it converts Arabic Presentation Forms (characters meant for visual rendering in old systems) back to their logical Unicode equivalents.

### 2b. Visual Reversal Detection & Fixing
A critical challenge for RTL text from some PDFs is that the text can be **character-reversed** (extracted right-to-left physically instead of logically).

```python
def is_reversed_arabic(text):
    # Checks for known words in their reversed form
    reversed_markers = ['هللا', 'دمحم', 'ىلع', 'نم', ...]
    count = sum(1 for marker in reversed_markers if marker in text)
    return count >= 1
```

If detected, the entire string is reversed back:
```python
text = text[::-1]
# Swap brackets too, as they flip direction under reversal
swaps = str.maketrans("()[]{}<>", ")(][}{><")
text = text.translate(swaps)
```

### 2c. Arabic-Specific Normalization
| Step | What it does | Why? |
|------|-------------|------|
| **Tashkeel removal** | Strips vowel marks (`ً ٌ ٍ ...`) | Reduces vocabulary size; improves semantic matching |
| **Hamza normalization** | `أ إ آ` → `ا` | "أحكام" and "احكام" become the same query-match |
| **Kashida removal** | Strips ـ | OCR artifact cleaning |
| **Arabic density check** | Filters pages with < 30% Arabic chars | Removes header/footer-only pages and garbage pages |

### 2d. Recursive Character Text Splitting
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,       # ~100-150 words per chunk
    chunk_overlap=100,    # Overlap to avoid cutting legal clauses mid-sentence
    separators=["\n\n", "\n", " ", ""]
)
```

**Why 600 characters?**
- Large enough to contain a complete legal ruling (fiqh principle + evidence).
- Small enough to be semantically specific for accurate vector search.

**Why 100-character overlap?**
- Fiqh texts often have rulings that span across sentence boundaries. Overlap prevents a ruling from being split across two chunks where neither is complete enough to answer a question.

---

## 🧠 Stage 3: Vector Embedding

**File**: `scripts/ingest.py`  
**Model**: [`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

### How embedding works:
Each text chunk is converted into a **384-dimensional vector** — a mathematical representation of its meaning.

```python
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embedding = model.encode(chunk["content"]).tolist()
# Result: [0.023, -0.512, 0.831, ...] (384 numbers)
```

### Why this model?
| Feature | Detail |
|---------|--------|
| **Multilingual** | Natively supports Arabic, English, and 50+ other languages |
| **Small & Fast** | Only 118MB — runs efficiently on Hugging Face free tier |
| **Semantic Quality** | Trained on paraphrase pairs; understands meaning, not just keywords |
| **384 dimensions** | Good balance between expressiveness and storage efficiency |

### Bulk Insert for Efficiency:
```python
execute_values(cur, "INSERT INTO chunks (book, page, content, embedding) VALUES %s", data)
```
Using `execute_values` batches all 4000+ rows into one database transaction instead of 4000 individual `INSERT` calls.

---

## 🗄️ Stage 4: Vector Database (pgvector)

**Database**: Neon PostgreSQL with [`pgvector`](https://github.com/pgvector/pgvector) extension

### Schema:
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chunks (
    id        SERIAL PRIMARY KEY,
    book      TEXT,
    page      INTEGER,
    content   TEXT,
    embedding vector(384)   -- The 384-dimensional vector column
);
```

### Why PostgreSQL + pgvector over dedicated vector DBs (Pinecone, Chroma)?
- **No vendor lock-in**: Standard SQL queries work alongside vector search.
- **Free Tier on Neon**: ServerLess PostgreSQL with pgvector included.
- **Metadata filtering**: Easy to filter by `book` or `page` with standard `WHERE` clauses alongside vector search.

---

## 🔎 Stage 5: Semantic Search (RAG Retrieval)

**File**: `app/main.py`

### The search algorithm — Cosine Similarity via `<=>` operator:
```sql
SELECT book, page, content,
       (embedding <=> %s::vector) AS distance
FROM chunks
ORDER BY distance ASC
LIMIT 5;
```

The `<=>` operator in pgvector calculates the **cosine distance** between two vectors:

```
cosine_distance = 1 - (A · B) / (|A| × |B|)
```

- **Distance = 0** → Identical meaning
- **Distance = 1** → Completely unrelated

The query returns the **5 most semantically similar chunks** to the user's question, regardless of whether they share keywords.

> **Example**: A user asks *"Can I pray without ablution if water is unavailable?"*, and the system finds chunks about *"التيمم"* (dry ablution) even though the word "tayammum" was never used in the question.

---

## 🤖 Stage 6: LLM Generation (Google Gemini)

**Model**: `gemini-2.5-flash`

### The Retrieval-Augmented Generation (RAG) flow:
```
User Question
      +
Top-5 Database Chunks (context)
      +
Custom Scholarly System Prompt (in Arabic)
      │
      ▼
  Gemini API
      │
      ▼
Structured Scholarly Answer
```

### The Scholarly System Prompt:
The AI is instructed to behave as a **Maliki scholar** (`فقيه مالكي`), not a generic chatbot. Key instructions include:
- Answer in a direct, scholarly (`رصين`) Arabic style.
- Use `<b>` tags around key legal terms (rendered in gold in the UI).
- Cite sources as *(Book Name, Page X)* within the answer.
- Provide a full *Sharh* (شرح/explanation), not just a summary.

---

## 📈 Performance & Scalability

| Metric | Value |
|--------|-------|
| Total chunks in DB | ~4,000+ |
| Embedding dimensions | 384 |
| Vector search time | < 100ms (pgvector indexed) |
| Gemini response time | 2-5 seconds |
| Embedding model size | 118 MB |

---

## 🛠️ Running the Full Pipeline Locally

```bash
# Step 1: Place your PDFs in data/raw/
# Step 2: Extract text from PDFs
python scripts/extract.py

# Step 3: Preprocess and chunk the text
python scripts/preprocess.py

# Step 4: Embed chunks and store in local PostgreSQL
python scripts/ingest.py

# Step 5: Migrate local DB to Neon (production)
python scripts/migrate_to_neon.py
```
