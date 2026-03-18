# 📊 Maliki AI Project Roadmap

This document outlines the step-by-step implementation of the Maliki AI Assistant.

## Phase 1: Data Acquisition & Preprocessing
- [ ] **Step 1.1**: Collect foundational Maliki PDF/Docx files.
- [ ] **Step 1.2**: Build a text extraction script using `PyMuPDF` (for PDFs).
- [ ] **Step 1.3**: Implement a "Page Tracker" to ensure every sentence is tied to its original page number.
- [ ] **Step 1.4**: Define a preprocessing pipeline (cleaning artifacts, normalize Arabic characters).

## Phase 2: Database & Embedding Pipeline
- [ ] **Step 2.1**: Set up a **PostgreSQL** instance and enable the `pgvector` extension.
- [ ] **Step 2.2**: Choose an embedding model (e.g., `sentence-transformers` for local or OpenAI).
- [ ] **Step 2.3**: Develop the **Upsert Script** to chunk data and push to Postgres.
- [ ] **Step 2.4**: Create indexes for both vector and keyword search (Hybrid Search).

## Phase 3: RAG Core Implementation (Qwen Integration)
- [ ] **Step 3.1**: Set up **Qwen-2.5** (using Ollama locally or a cloud API).
- [ ] **Step 3.2**: Design a scholarly **System Prompt** for Maliki Fiqh contexts.
- [ ] **Step 3.3**: Implement the retrieval chain (Query -> Vector Search -> Context Assembly).

## Phase 4: Backend API (FastAPI)
- [ ] **Step 4.1**: Initialize **FastAPI** project structure.
- [ ] **Step 4.2**: Implement endpoints for `GET /books`, `POST /ask`, and `GET /sources`.
- [ ] **Step 4.3**: Implement authentication for admin (uploading new books).

## Phase 5: Frontend UI
- [ ] **Step 5.1**: Build a premium chat interface (HTML + Tailwind CSS).
- [ ] **Step 5.2**: Add a "Source Preview" feature to show the original text snippets upon clicking a citation.
- [ ] **Step 5.3**: Optimize for Arabic RTL (Right-to-Left) text rendering.

## Phase 6: Testing & Deployment
- [ ] **Step 6.1**: Create a testing suite with specific Fiqh cases (e.g., *Zakat*, *Salah* rulings).
- [ ] **Step 6.2**: Dockerize the entire stack (Postgres + Python API + Frontend).
- [ ] **Step 6.3**: Deploy to cloud (AWS, Azure, or DigitalOcean).
