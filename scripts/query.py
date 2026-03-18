import os
import psycopg2
import google.generativeai as genai
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

# Load Embedding Model (Same one used for ingestion)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
print(f"🧠 Loading embedding model...")
embed_model = SentenceTransformer(MODEL_NAME)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def search_database(query_text, top_k=5):
    """
    Performs a vector similarity search in PostgreSQL.
    """
    # 1. Generate embedding for the question
    query_vector = embed_model.encode(query_text).tolist()
    
    # 2. Query Postgres
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Using pgvector <=> operator (cosine distance)
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

def ask_maliki_ai(question):
    """
    Main RAG function: Retrieve -> Prompt -> Generate
    """
    # 1. Search for relevant context
    print(f"🔍 Searching for classical Maliki evidence...")
    context_chunks = search_database(question)
    
    if not context_chunks:
        return "Sorry, I couldn't find any relevant information in the provided books."

    # 2. Format context for the LLM
    context_text = "\n\n".join([
        f"Source: [{res[0]}, Page {res[1]}]\nContent: {res[2]}" 
        for res in context_chunks
    ])

    # 3. Create the scholarly prompt
    system_instruction = (
        "You are an expert Maliki Faqih (scholar of Maliki jurisprudence). "
        "Your goal is to answer questions strictly based on the provided context from classical Maliki texts. "
        "Always cite the book name and page number for your claims. "
        "If the answer is not in the context, say that you don't know based on the available books. "
        "Answer in the same language as the question (Arabic or English)."
    )

    full_prompt = f"{system_instruction}\n\nCONTEXT:\n{context_text}\n\nQUESTION: {question}"

    # 4. Generate response using Gemini
    print(f"🤖 Consulting Gemini 2.5 Flash...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(full_prompt)

    return response.text, context_chunks

if __name__ == "__main__":
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_key_here":
        print("❌ Error: GEMINI_API_KEY not found in .env file.")
    else:
        while True:
            user_question = input("\n🕌 Ask the Maliki Assistant (or type 'exit'): ")
            if user_question.lower() in ["exit", "quit", "q"]:
                break
                
            answer, sources = ask_maliki_ai(user_question)
            
            print("\n" + "="*50)
            print(f"📖 ANSWER:\n{answer}")
            print("="*50)
            print("📚 SOURCES USED:")
            for s in sources:
                print(f"- {s[0]} (Page {s[1]})")
