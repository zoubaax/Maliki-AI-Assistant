import os
import json
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load database credentials from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "maliki_ai")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword")
DB_PORT = os.getenv("DB_PORT", "5432")

# Choose an embedding model (this one is small, fast, and multilingual)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
print(f"🧠 Loading embedding model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def setup_database():
    """
    Initializes the database with pgvector extension and the chunks table.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Enable pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # 2. Create chunks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            book TEXT,
            page INT,
            content TEXT,
            embedding vector(384)
        );
    """)
    
    # 3. Clear existing data (to avoid duplicates when re-ingesting)
    print("🧹 Clearing old data for a fresh start...")
    cur.execute("TRUNCATE TABLE chunks;")
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database schema initialized with pgvector.")

def ingest_data(json_path):
    """
    Reads chunks from JSON, generates embeddings, and saves to Postgres.
    """
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found. Run preprocess.py first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    conn = get_db_connection()
    cur = conn.cursor()

    print(f"🚀 Starting ingestion of {len(chunks)} chunks...")
    
    processed_data = []
    for chunk in chunks:
        # Generate the vector embedding for the content
        embedding = model.encode(chunk["content"]).tolist()
        
        processed_data.append((
            chunk["book"],
            chunk["page"],
            chunk["content"],
            embedding
        ))

    # Bulk insert for efficiency
    insert_query = "INSERT INTO chunks (book, page, content, embedding) VALUES %s"
    execute_values(cur, insert_query, processed_data)

    conn.commit()
    cur.close()
    conn.close()
    print(f"🎉 Successfully ingested {len(chunks)} chunks into the database!")

if __name__ == "__main__":
    setup_database()
    ingest_data("data/processed/chunks.json")
