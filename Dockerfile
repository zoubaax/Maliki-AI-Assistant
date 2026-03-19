# Optimized Backend-Only Dockerfile for Hugging Face Spaces (Vercel Split)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for psycopg2 & SSL)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies (including sentence-transformers & torch)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY app/ ./app
COPY scripts/ ./scripts
COPY .env . 

# Expose Hugging Face Default Port (7860)
EXPOSE 7860

# Start FastAPI server on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
