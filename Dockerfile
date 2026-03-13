FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Pre-build ChromaDB vector store during image build
RUN python build_vectorstore.py

# Render injects PORT env var; default to 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
