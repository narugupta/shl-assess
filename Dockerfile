# ──────────────────────────────────────────────────────────────
# Single-stage build
#
# Why not multi-stage?
# sentence-transformers (PyTorch) was replaced with fastembed
# (ONNX Runtime) to stay inside Render's 512 MB free-tier RAM
# limit. The resulting image is small enough that a single stage
# is simpler without losing meaningful size benefit.
#
# Why pre-compute embeddings at build time?
# The Retriever reads data/processed/embeddings.npy on startup.
# Baking it into the image means every cold start is just an
# in-memory FAISS load (~1 s) rather than a full encode run.
# ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# fastembed downloads the ONNX model to FASTEMBED_CACHE_PATH.
# Pinning it inside /app keeps it under the appuser chown below.
ENV FASTEMBED_CACHE_PATH=/app/.cache/fastembed
ENV PORT=8000

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Pre-download the ONNX embedding model at build time so the
# container never makes outbound model-download calls at runtime.
RUN python - <<'EOF'
from fastembed import TextEmbedding
model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
list(model.embed(["warmup"]))
print("Embedding model cached.")
EOF

# Copy application source and data (knowledge base + raw catalog)
COPY app/       ./app/
COPY data/      ./data/
COPY frontend/  ./frontend/

# Pre-compute and cache embeddings into data/processed/embeddings.npy.
# Only the Retriever is instantiated here; no GROQ_API_KEY is needed.
RUN python - <<'EOF'
from app.retrieval.retriever import Retriever
print("Pre-computing embeddings...")
Retriever()
print("Embeddings cached.")
EOF

# Non-root user for security; chown covers model cache + embeddings
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn app.api.app:app --host 0.0.0.0 --port ${PORT}"]
