# 🕌 Maliki AI Assistant

A sophisticated **Retrieval-Augmented Generation (RAG)** system designed specifically for **Maliki Fiqh** (Islamic Jurisprudence). This project leverages state-of-the-art AI models to provide accurate, scholarly answers grounded in classical foundational texts.

## 🚀 Key Features

*   **Verified Knowledge**: Answers are strictly grounded in canonical Maliki texts (e.g., *Taqrib al-Fiqh al-Maliki*, *Mukhtasar al-Akhdari*).
*   **Scholarly Explanations**: Provides deep "Sharh" (detailed explanation) of rulings rather than just literal quotes.
*   **Automatic Citations**: Every answer includes the book title and page number for immediate verification.
*   **Premium UI**: A high-end, dark-themed scholarly interface designed for religious study.

## 🧠 Core Algorithms & Implementation

This system uses a custom-built pipeline optimized for the complexities of Arabic legal texts:

### 1. Advanced Arabic Preprocessing
*   **Unicode Normalization (NFKC)**: Corrects Arabic presentation forms (e.g., combined letters like 'LA') to standard Unicode for accurate indexing.
*   **Visual Reversal Correction**: Heuristic detection and fixing of visually reversed Arabic text often found in older PDF extracts.
*   **Noise Filtering**: Custom regex patterns to remove OCR artifacts and Latin sequences without damaging the Fiqh notation.

### 2. Semantic Chunking & Storage
*   **Recursive Character Splitting**: Chunks the text into semantic segments (~600 chars) with 15% overlap to maintain context across split points.
*   **Vector Embeddings**: Uses `paraphrase-multilingual-MiniLM-L12-v2` to capture the deep semantic meaning of Arabic legal terms.
*   **Vector Database**: High-performance storage in **PostgreSQL** using the `pgvector` extension.

### 3. Retrieval & Generation (RAG)
*   **Vector Search**: Uses **Cosine Similarity** (`<=>` operator) to find the most relevant contextual passages from the library.
*   **Contextual Prompting**: A scholarly system instruction that forces the LLM (Gemini) to act as a Maliki "Muhaqqiq" (Verifying Scholar).
*   **Factuality Guard**: The model is restricted from providing information outside the provided canonical context.

## 🛠️ Technology Stack

| Layer          | Technology                          |
| -------------- | ----------------------------------- |
| **LLM**        | Google Gemini 1.5/2.5 Flash         |
| **Vector DB**  | PostgreSQL + `pgvector`             |
| **Backend**    | FastAPI (Python 3.9+)               |
| **Embeddings** | Paraphrase Multilingual MiniLM L12  |
| **Frontend**   | HTML5 + Tailwind CSS + Vanilla JS   |
| **ORM**        | `psycopg2` (RAW SQL for performance)|

## 🏗️ Technical Architecture

1.  **Ingestion**: PDFs are extracted with Unicode normalization (NFKC) to ensure searchability.
2.  **Indexing**: Normalized chunks are embedded and stored in PostgreSQL with metadata.
3.  **Inference**: User queries are vectorized and matched against the DB using semantic similarity.
4.  **Synthesis**: The retrieved "Context" + "Question" are sent to Gemini with a scholarly prompt.
5.  **Output**: A clean, formatted Arabic response with bold headings and precise citations.

