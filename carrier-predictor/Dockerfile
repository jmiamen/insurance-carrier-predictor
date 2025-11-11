# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY .env.example .env

# Copy carrier data files
COPY data/ ./data/

# Create index directory
RUN mkdir -p data/index

# Download embedding model at build time (optional, speeds up first run)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Build knowledge base
RUN python scripts/update_kb.py --path data --rebuild

# Copy frontend build from frontend-builder stage
COPY --from=frontend-builder /frontend/build ./frontend/build

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
