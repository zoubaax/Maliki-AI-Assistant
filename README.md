# 🕌 Maliki AI Assistant

A sophisticated **Retrieval-Augmented Generation (RAG)** system designed specifically for **Maliki Fiqh** (Islamic Jurisprudence). This project leverages state-of-the-art AI models to provide accurate, cited answers from a library of Maliki foundational texts.

## 🚀 Key Features

*   **Verified Knowledge**: Answers are grounded in classical Maliki texts (like *Al-Muwatta*, *Risala al-Qayrawani*, etc.).
*   **Automatic Citations**: Every answer includes the book title and page number for verification.
*   **Qwen-2.5 Powered**: High-performance LLM optimized for scholarly Arabic and technical Islamic terms.
*   **Vector Search**: Uses **PostgreSQL (pgvector)** for blistering fast semantic retrieval.
*   **Hybrid Search**: Combines semantic embeddings with keyword search for maximum precision.

## 🛠️ Technology Stack

| Layer          | Technology                          |
| -------------- | ----------------------------------- |
| **LLM**        | Gemini 2.5 Flash (Initial Engine) / Qwen-2.5 |
| **Database**   | PostgreSQL + `pgvector`             |
| **Framework**  | FastAPI (Python)                    |
| **Orchestration**| LangChain / LlamaIndex              |
| **Frontend**   | HTML + Tailwind CSS (Vanilla JS)   |
| **Embeddings** | BGE-M3 / OpenAI / HuggingFace       |

---

## 🏗️ Architecture

1.  **Ingestion**: PDFs/Word files are chunked into semantic segments.
2.  **Indexing**: Chunks are embedded and stored in **PostgreSQL** alongside metadata.
3.  **Retrieval**: User queries are vectorized to find the top $k$ relevant passages.
4.  **Augmentation**: Gemini 2.5 Flash receives the user's question + relevant passages as context.
5.  **Generation**: Gemini generates a scholarly answer with precise book/page references.
