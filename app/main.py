import os
import psycopg2
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load configuration
load_dotenv()

# Database Config
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "maliki_ai")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword")
DB_PORT = os.getenv("DB_PORT", "5432")

# API Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Load Embedding Model
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embed_model = SentenceTransformer(MODEL_NAME)

app = FastAPI(title="Maliki AI Assistant")

# Setup Templates
templates = Jinja2Templates(directory="app/templates")

class QueryRequest(BaseModel):
    question: str

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

    # 3. Prompt (Direct & Structured)
    system_instruction = (
        "أنت فقيه مالكي محقق. قدم جواباً فقهياً مركزاً وشاملاً. "
        "ادخل في صلب المسألة مباشرة دون مقدمات. "
        "استخدم تنسيق الماركدوان (مثل النقاط • والعناوين الفرعية العريضة) لتنظيم الإجابة بصرياً. "
        "يجب البدء بسطر جديد تماماً لكل نقطة (•) ولكل فكرة جديدة لضمان الوضوح والرتابة. "
        "التزم فقط بالنصوص المرفقة في السياق واذكر رقم الصفحة."
    )
    
    full_prompt = f"{system_instruction}\n\nالنصوص الفقهية (السياق):\n{context_text}\n\nالمسألة: {request.question}"

    # 4. Gemini Call
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(full_prompt)

    # 5. Build Response
    sources = [{"book": res[0], "page": res[1], "snippet": res[2][:150] + "..."} for res in context_chunks]
    
    return {"answer": response.text, "sources": sources}
