import os
import psycopg2
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load configuration
load_dotenv()

# Database Config (Neon support)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:mypassword@db:5432/maliki_ai")
if not DATABASE_URL.endswith("sslmode=require") and "neon.tech" in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

# API Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Load Embedding Model
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embed_model = SentenceTransformer(MODEL_NAME)

app = FastAPI(title="Maliki AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def search_database(query_text, top_k=5):
    query_vector = embed_model.encode(query_text).tolist()
    conn = get_db_connection()
    cur = conn.cursor()
    search_query = """
        SELECT book, page, content, 
               (embedding <=> %s::vector) AS distance
        FROM chunks
        ORDER BY distance ASC
        LIMIT %s;
    """
    cur.execute(search_query, (query_vector, top_k))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

# Static Files (Production)
# Mounting static files at /assets for Vite build
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # In production, serve frontend/dist/index.html
    # In development, this won't be called if you use Vite's proxy
    index_path = "frontend/dist/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>Maliki AI Backend is running. Frontend not found in 'frontend/dist'.</h3>"

@app.post("/ask")
async def ask_maliki_ai(request: QueryRequest):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_key_here":
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")

    # 1. Search Context
    context_chunks = search_database(request.question)
    
    if not context_chunks:
        return {"answer": "I couldn't find relevant information.", "sources": []}

    # 2. Format Context
    context_text = "\n\n".join([
        f"Source: [{res[0]}, Page {res[1]}]\nContent: {res[2]}" 
        for res in context_chunks
    ])

    # 3. Enhanced Scholarly Prompt (Enforces the "Perfect" look)
    system_instruction = (
        "أنت فقيه مالكي جليل ومدرّس خبير في المتون. أجب بأسلوب العلماء الربانيين: رصين، مباشر، وخالٍ من العبارات المدرسية الجافة.\n\n"
        "**قواعد التنسيق والشرح:**\n"
        "1. **الدخول المباشر**: ابدأ بالبسملة أو الحمدلة، ثم ادخل في صلب المسألة مباشرة.\n"
        "2. **العناوين العريضة (بأسلوب المتون)**: استخدم <b>• العبارة الفقهية المركزية:</b> في بداية كل حكم.\n"
        "3. **الشرح المستفيض (Sharh)**: لا تكتفِ بتلخص المتن، بل كن **شارحاً متمكناً**؛ فكك الألفاظ، وضح الحالات المختلفة، اشرح الشروط والقيود، واجعل السائل يخرج بفهم عميق للمسألة (توسع في الشرح بأسلوب تعليمي).\n"
        "4. **التوثيق الدقيق**: في نهاية كل فقرة، اذكر (اسم الكتاب، ص X) بوقار.\n"
        "5. **نظافة النص**: تجنب المقدمات الطويلة والمؤخرات الزائدة. اجعل النص كأنه صفحة من كتاب 'شرح متن' محقق."
    )




    
    full_prompt = f"{system_instruction}\n\nالنصوص الفقهية (السياق):\n{context_text}\n\nالمسألة: {request.question}"

    # 4. Gemini Call
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(full_prompt)

    # 5. Build Response
    sources = [{"book": res[0], "page": res[1], "snippet": res[2][:150] + "..."} for res in context_chunks]
    
    return {"answer": response.text, "sources": sources}
