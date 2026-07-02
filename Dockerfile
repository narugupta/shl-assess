# ──────────────────────────────────────────────────────────────
# Stage 1: dependency builder
# ──────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System libs needed to compile faiss-cpu and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ──────────────────────────────────────────────────────────────
# Stage 2: model pre-download
#   Baking the sentence-transformers weights into the image means
#   the container never has to download them at runtime, which
#   keeps every cold start inside Render's 2-minute readiness
#   window regardless of network conditions.
# ──────────────────────────────────────────────────────────────
FROM python:3.11-slim AS model-cache

COPY --from=builder /install /usr/local

RUN python - <<'EOF'
from sentence_transformers import SentenceTransformer
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("Model downloaded and cached.")
EOF


# ──────────────────────────────────────────────────────────────
# Stage 3: runtime image
# ──────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# libgomp1 is a runtime dependency of faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy Hugging Face model cache so cold starts skip the download
COPY --from=model-cache /root/.cache /root/.cache

# Copy application source
COPY app/       ./app/
COPY data/      ./data/
COPY frontend/  ./frontend/

# Pre-computed embeddings live in data/processed/embeddings.npy.
# The Retriever._load_or_build_embeddings() method will load them
# on startup instead of recomputing (~60 s saved per cold start).

# Render injects PORT at runtime; default to 8000 for local use.
ENV PORT=8000

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app /root/.cache
USER appuser

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn app.api.app:app --host 0.0.0.0 --port ${PORT}"]
