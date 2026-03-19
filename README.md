# 🕌 Maliki AI Assistant

> An AI-powered Islamic Fiqh research assistant specialized in the **Maliki school of jurisprudence**, built with a full RAG (Retrieval-Augmented Generation) pipeline.

[![Frontend](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel)](https://maliki-ai-assistant.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-Hugging%20Face-yellow?logo=huggingface)](https://huggingface.co/spaces/zoubaax/Maliki-Assistant)
[![Database](https://img.shields.io/badge/Database-Neon%20PostgreSQL-blue?logo=postgresql)](https://neon.tech)
[![Technical Docs](https://img.shields.io/badge/Docs-Technical%20Deep%20Dive-green)](./TECHNICAL.md)

---

## ✨ Features

- 🔍 **Semantic Search** — Searches through thousands of scholarly chunks from Maliki Fiqh books using vector embeddings.
- 📖 **Source Citations** — Every answer includes the **book title** and **page number** so you can verify the source.
- 🌟 **Gold-Highlighted Wisdom** — Important terms and rulings are highlighted in a beautiful scholarly gold color.
- 📱 **Fully Responsive** — Works beautifully on both desktop and mobile.
- ⚡ **Fast RAG Pipeline** — Retrieves the most relevant passages before generating an answer with Google Gemini.

---

## 🏗️ Architecture

```
User (Browser)
    │
    ▼
┌──────────────────┐
│   Vercel (React) │  ← Premium UI with gold styling
│   Frontend       │
└────────┬─────────┘
         │ HTTPS POST /ask
         ▼
┌──────────────────────────┐
│  Hugging Face Space      │  ← FastAPI backend (Docker)
│  FastAPI + RAG Pipeline  │
└────────┬─────────────────┘
         │ Vector Search
         ▼
┌──────────────────────┐
│  Neon PostgreSQL     │  ← Cloud database with pgvector
│  + pgvector          │     (4000+ scholarly chunks)
└──────────────────────┘
         │ Context
         ▼
┌──────────────────────┐
│  Google Gemini API   │  ← Generates the final answer
└──────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Framer Motion |
| **Backend** | FastAPI, Python 3.11 |
| **AI Model** | Google Gemini 2.5 Flash |
| **Embeddings** | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| **Database** | Neon PostgreSQL + pgvector |
| **Frontend Hosting** | Vercel |
| **Backend Hosting** | Hugging Face Spaces (Docker) |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Neon PostgreSQL database
- A Google Gemini API key

### 1. Clone the Repository
```bash
git clone https://github.com/zoubaax/Maliki-AI-Assistant.git
cd Maliki-AI-Assistant
```

### 2. Backend Setup
```bash
# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create your .env file (copy the template below)
cp .env.example .env
# Fill in your DATABASE_URL and GEMINI_API_KEY

# Run the backend
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create frontend .env
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Run the frontend
npm run dev
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory with:

```env
# Neon PostgreSQL Connection String
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

For the **frontend**, create `frontend/.env`:
```env
# URL of your deployed backend
VITE_API_BASE_URL=https://your-space.hf.space
```

> ⚠️ **Never commit your `.env` files!** They are already excluded in `.gitignore`.

---

## 📂 Project Structure

```
maliki-ai-assistant/
├── app/
│   └── main.py          # FastAPI backend & RAG logic
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main chat interface
│   │   └── index.css    # Scholarly design system
│   └── index.html
├── scripts/
│   ├── extract.py       # Extract text from PDFs
│   ├── ingest.py        # Generate and store embeddings
│   ├── preprocess.py    # Clean and chunk the text
│   └── migrate_to_neon.py  # Migrate local DB to Neon cloud
├── Dockerfile           # For Hugging Face deployment
├── requirements.txt
└── README.md
```

---

## 📜 License

This project is open-source and available under the **MIT License**.

---

## 🤲 Acknowledgments

Built with love and respect for Islamic scholarship. May it be a benefit to all who seek knowledge.

*"طلب العلم فريضة على كل مسلم"*
> "Seeking knowledge is an obligation upon every Muslim." — Prophet Muhammad ﷺ
