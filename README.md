# SHL Conversational Assessment Recommender

A conversational agent that guides hiring managers from a vague intent to a grounded shortlist of SHL assessments through multi-turn dialogue.

**Live API**: `https://shl-assess-ty4a.onrender.com`

---

## API Reference

### `GET /health`
Readiness check. Returns HTTP 200 when the service is ready.

```json
{"status": "ok"}
```

### `POST /chat`
Stateless conversational endpoint. Every call carries the full conversation history.

**Request**
```json
{
  "messages": [
    {"role": "user",      "content": "Hiring a mid-level Java developer"},
    {"role": "assistant", "content": "What seniority level are you targeting?"},
    {"role": "user",      "content": "Mid-level, around 4 years experience"}
  ]
}
```

**Response**
```json
{
  "reply": "Here are 5 assessments suited for a mid-level Java developer.",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/solutions/products/product-catalog/view/java-8-new/",
      "test_type": "K"
    }
  ],
  "end_of_conversation": false
}
```

| Field | Type | Notes |
|---|---|---|
| `reply` | string | LLM-generated explanation grounded in catalog data |
| `recommendations` | array | Empty while clarifying; 1–10 items when committed |
| `end_of_conversation` | boolean | `true` only when the agent considers the task complete |
| `test_type` | string | `K` Knowledge · `A` Ability · `P` Personality · `S` Simulation · `C` Competency · `O` Other |

---

## Conversational Behaviors

| Behavior | Example |
|---|---|
| **Clarify** | `"I need an assessment"` → asks for role before retrieving |
| **Recommend** | `"Hiring a senior Java dev"` → returns grounded shortlist |
| **Refine** | `"Actually, add a personality test"` → updates shortlist without resetting |
| **Compare** | `"What's the difference between OPQ and GSA?"` → grounded diff from catalog |
| **Refuse** | Off-topic, legal questions, prompt injection → empty recommendations + explanation |

---

## Local Development

### Prerequisites
- Python 3.11+
- A [Groq API key](https://console.groq.com/keys) (free tier)

### Setup

```bash
git clone https://github.com/narugupta/shl-assess.git
cd shl-assess

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create `.env` (never commit this):
```
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### Run

```bash
uvicorn app.api.app:app --reload
```

Service is available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

> **First run**: `data/processed/embeddings.npy` is not tracked in git. It is computed automatically on first startup and cached for subsequent runs (~30 s with fastembed/ONNX).

---

## Docker

```bash
# Build (pre-downloads model & pre-computes embeddings at build time)
docker build -t shl-recommender .

# Run
docker run --rm -p 8000:8000 -e GROQ_API_KEY=your_key shl-recommender
```

---

## Deploy to Render

The repo includes a [`render.yaml`](render.yaml) for one-click deployment.

1. Push the repo to GitHub.
2. Go to [render.com](https://render.com) → **New → Web Service** → connect your repo.
3. Render auto-detects `render.yaml` and uses the `Dockerfile`.
4. In the Render dashboard → **Environment** tab, set `GROQ_API_KEY`.
5. Click **Deploy**.

> **Free tier note**: The container sleeps after ~15 minutes of inactivity. First request after sleep takes up to 90 s. The SHL evaluator allows a 2-minute cold-start window.

---

## Evaluation

### Live scenario tests (requires running service)

```bash
# Against localhost
python test_chat_quality.py

# Against deployed instance
python test_chat_quality.py --base-url https://shl-assess-ty4a.onrender.com

# Single category
python test_chat_quality.py --category refusal

# List all scenarios
python test_chat_quality.py --list
```

Checks schema compliance, turn cap, refusal consistency, clarification behavior, and refinement continuity across 30+ scenarios.

### Offline Recall@10 against gold traces

```bash
python scripts/evaluate_traces.py tests/traces/GenAI_SampleConversations
```

Replays all 10 public conversation traces through the real pipeline (LLM stubbed) and reports:
- **Hard evals**: schema compliance, catalog-only URLs, turn cap honored
- **Recall@10**: fraction of gold-labeled assessments in the top-10 shortlist
- **Behavior probes**: no recommendation on vague turn 1, refinement extends shortlist, off-topic refused

### Unit tests

```bash
pytest tests/ -v
```

40+ modules covering guards, planner, retrieval, generation, and API endpoints.

---

## Architecture

```
POST /chat (full history)
        │
        ▼
   GuardEngine          — blocks injection, off-topic, legal, oversized
        │
        ▼
   Planner              — extracts slots: role, seniority, language,
        │                 duration, skills, categories, comparison items
        ▼
   Clarifier            — requires `role` before retrieval
        │
        ▼
   DecisionEngine       — routes: RETRIEVE / COMPARE / GREETING /
        │                 SHOW_HELP / REJECT / UNKNOWN
        ▼
   HybridRetriever      — BM25 (0.5) + FAISS (0.5), then filter + re-rank
        │
        ▼
   ContextBuilder       — formats top-10 docs for the LLM prompt
        │
        ▼
   LLMGenerator         — Groq llama-3.3-70b-versatile, temp 0.2
        │                 COMPARE → comparison template (no shortlist)
        │                 RETRIEVE → recommend template
        ▼
   Verifier             — flags hallucinated names / URLs / duplicates
        │
        ▼
   ChatResponse         — reply · recommendations · end_of_conversation
```

### Stack

| Layer | Choice | Reason |
|---|---|---|
| API | FastAPI + Uvicorn | Fast, async, auto-docs |
| LLM | Groq `llama-3.3-70b-versatile` | Free tier, ~1 s latency |
| Embeddings | `fastembed` (ONNX) | ~120 MB RAM vs ~500 MB for PyTorch; fits Render free tier |
| Vector search | FAISS `IndexFlatIP` | In-memory, no server needed |
| Keyword search | BM25 (`rank-bm25`) | Catches exact skill/product names |
| Deploy | Docker + Render | Free, Docker-native |

---

## Project Structure

```
app/
  api/          FastAPI app, routes, models, pipeline
  generation/   Prompts, LLM generator, verifier, formatter
  planner/      Intent, slot extraction, guards, clarifier, decision
  retrieval/    Loader, embedder, FAISS, BM25, hybrid, filters, ranker
data/
  processed/    knowledge_base.json, documents.json
  raw/          shl_catalog.json
tests/          40+ pytest modules + 10 gold conversation traces
scripts/        evaluate_traces.py (offline Recall@10 harness)
Dockerfile      Single-stage; pre-downloads model & embeddings at build
render.yaml     Render deployment config
```
