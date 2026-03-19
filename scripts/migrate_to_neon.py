import json
import psycopg2
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load config
load_dotenv()

# Neon Database URL — loaded from .env file (never hardcode!)
NEON_DB_URL = os.getenv("DATABASE_URL")
if not NEON_DB_URL:
    raise ValueError("❌ DATABASE_URL is not set. Please add it to your .env file.")
NEON_DB_URL = NEON_DB_URL.strip()

# Path to the chunks (from ingest.py output)
CHUNKS_FILE = "data/processed/chunks.json"

def migrate():
    print("🚀 Initializing Migration to Neon (Production)...")
    
    # 1. Load Chunks
    if not os.path.exists(CHUNKS_FILE):
        print(f"❌ Error: {CHUNKS_FILE} not found. Run ingest.py first.")
        return

    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"📖 Loaded {len(chunks)} scholarly chunks from local storage.")

    # 2. Load Embedding Model
    print("🧠 Initializing Embedding Model (MiniLM-L12)...")
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    # 3. Connect to Neon
    try:
        conn = psycopg2.connect(NEON_DB_URL)
        cur = conn.cursor()
        print("✅ Successfully connected to Neon Cloud Database.")

        # 4. Setup Table & PgVector
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("DROP TABLE IF EXISTS chunks;")
        cur.execute("""
            CREATE TABLE chunks (
                id SERIAL PRIMARY KEY,
                book TEXT,
                page INTEGER,
                volume TEXT,
                content TEXT,
                embedding vector(384)
            );
        """)
        print("🏗️ Recreated production table with pgvector support.")

        # 5. Insert Data
        print("📥 Migrating chunks (this may take a few minutes)...")
        for i, chunk in enumerate(chunks):
            vector = model.encode(chunk['content']).tolist()
            cur.execute(
                "INSERT INTO chunks (book, page, content, embedding) VALUES (%s, %s, %s, %s)",
                (chunk['book'], chunk['page'], chunk['content'], vector)
            )
            if (i + 1) % 100 == 0:
                print(f"✅ Migrated {i+1}/{len(chunks)} chunks...")

        conn.commit()
        cur.close()
        conn.close()
        print("🎉 MIGRATION COMPLETE! Your Maliki AI is now backed by Neon Cloud.")

    except Exception as e:
        print(f"❌ Migration Error: {e}")

if __name__ == "__main__":
    migrate()
