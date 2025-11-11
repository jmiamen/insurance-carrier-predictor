# Carrier Predictor

Production-ready Python API that predicts the best life insurance carriers/products for clients using a knowledge-driven RAG approach.

## Features

- **Knowledge-Driven**: Uses RAG (Retrieval-Augmented Generation) with carrier product documents
- **Local Embeddings**: Works out-of-the-box with `sentence-transformers` (no API keys required)
- **HIPAA-Friendly**: PHI-safe logging with PII/PHI redaction
- **Modular Architecture**: Clean service layer with testable components
- **Production-Ready**: FastAPI with proper config management, error handling, and tests

## Quick Start

### 1. Setup

```bash
# Clone/navigate to project
cd carrier-predictor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env if needed (defaults work out-of-the-box)
```

### 2. Ingest Knowledge Base

Place your carrier PDFs/HTML files in `data/carriers/`, then build the index:

```bash
# CLI method (recommended for initial setup)
python scripts/update_kb.py --path data/carriers

# Or via API (after starting server)
curl -X POST http://localhost:8000/kb/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "data/carriers"}'
```

### 3. Start Server

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: http://localhost:8000

API docs: http://localhost:8000/docs

### 4. Get Recommendations

```bash
curl -X POST http://localhost:8000/recommend-carriers \
  -H "Content-Type: application/json" \
  -d '{
    "age": 62,
    "state": "TX",
    "gender": "F",
    "smoker": false,
    "coverage_type": "Whole Life",
    "desired_coverage": 250000,
    "health_conditions": ["diabetes", "neuropathy"]
  }'
```

**Sample Response:**

```json
{
  "recommendations": [
    {
      "carrier": "Mutual of Omaha",
      "product": "Living Promise Whole Life",
      "confidence": 0.91,
      "reason": "Accepts controlled diabetes; TX eligible; age within band 45–85.",
      "portal_url": "https://sales.mutualofomaha.com/agent/login"
    },
    {
      "carrier": "Elco Mutual",
      "product": "Golden Eagle Whole Life",
      "confidence": 0.88,
      "reason": "Diabetes tolerance and TX eligibility; product aligns with FE needs.",
      "portal_url": "https://elcomutual.com/agent-portal"
    }
  ]
}
```

## Project Structure

```
carrier-predictor/
├── README.md
├── .env.example
├── requirements.txt
├── Dockerfile
├── pyproject.toml
├── src/
│   ├── app.py                    # FastAPI application
│   ├── routers/
│   │   ├── predict.py            # POST /recommend-carriers
│   │   └── kb.py                 # POST /kb/ingest
│   ├── schemas/
│   │   ├── client_input.py       # Request validation
│   │   ├── recommendation.py     # Response models
│   │   └── ingest.py             # Ingest request model
│   ├── services/
│   │   ├── config.py             # Environment config
│   │   ├── logging_setup.py      # PHI-safe logging
│   │   ├── portals.py            # Portal URL mapping
│   │   ├── kb_loader.py          # PDF/HTML extraction
│   │   ├── embedder.py           # FAISS index management
│   │   ├── retriever.py          # Similarity search
│   │   ├── rules.py              # Eligibility filters
│   │   ├── scorer.py             # Confidence scoring
│   │   └── ranker.py             # Result ranking
│   └── config/
│       ├── carriers.yaml         # Carrier eligibility rules
│       └── portal_links.json     # Portal URLs
├── data/
│   ├── carriers/                 # Put PDFs/HTML here (gitignored)
│   └── index/                    # FAISS index (gitignored)
├── scripts/
│   └── update_kb.py              # CLI: rebuild index
└── tests/
    ├── test_predict.py
    ├── test_rules.py
    └── test_retriever.py
```

## Configuration

### Environment Variables (.env)

```bash
# Embedding Model
EMBED_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# Data Directories
INDEX_DIR=data/index
DOCS_DIR=data/carriers

# Optional: OpenAI Integration
OPENAI_API_KEY=
ENABLE_OPENAI_SCORING=false

# Logging
LOG_LEVEL=INFO
```

### Carrier Rules (config/carriers.yaml)

Define carrier eligibility by state, age, product type, and health tolerance:

```yaml
MutualOfOmaha:
  states: ["TX", "FL", "GA"]
  portal_url: "https://sales.mutualofomaha.com/agent/login"
  products:
    LivingPromise:
      type: "Whole Life"
      min_age: 45
      max_age: 85
      smoker: true
      health_tolerance: ["diabetes controlled"]
```

## API Endpoints

### POST /recommend-carriers

Get carrier/product recommendations.

**Request:**
```json
{
  "age": 62,
  "state": "TX",
  "gender": "F",
  "smoker": false,
  "coverage_type": "Whole Life",
  "desired_coverage": 250000,
  "health_conditions": ["diabetes", "neuropathy"],
  "notes": "optional free text"
}
```

**Response Fields:**
- `carrier`: Insurance carrier name
- `product`: Specific product name
- `confidence`: Score 0-1 (higher = better match)
- `reason`: Human-readable explanation
- `portal_url`: Agent portal link (if available)

### POST /kb/ingest

Rebuild knowledge base index from documents.

**Request:**
```json
{
  "path": "data/carriers"
}
```

**Response:**
```json
{
  "indexed_files": 15,
  "chunks": 342
}
```

### GET /health

Health check endpoint.

## Security & Compliance

### PHI-Safe Logging

- **No raw PII/PHI in logs**: Client health conditions are logged as counts only
- **Request IDs**: All operations use hashed request IDs for tracing
- **Redaction**: Sensitive fields automatically redacted in log output

Example log:
```
INFO [req_a3f2e1] Received recommendation request: age=62, state=TX, conditions_count=2
```

### Best Practices

- Health data never persists beyond request lifecycle
- Use environment variables for all secrets
- Rotate logs regularly (configure via logging_setup.py)
- Deploy behind authentication/authorization layer

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
ruff check src/ tests/
```

### Docker Deployment

```bash
# Build image
docker build -t carrier-predictor .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=sk-... \
  carrier-predictor
```

## How It Works

### Scoring Algorithm

1. **Rule-Based Filtering** (`rules.py`):
   - Check state eligibility
   - Verify age band compatibility
   - Match product type (Term/Whole Life/IUL)
   - Assess health tolerance

2. **Retrieval Scoring** (`retriever.py`):
   - Embed client profile
   - Search FAISS index for similar documents
   - Boost scores for carriers mentioned in top results

3. **Combined Score** (`scorer.py`):
   - Base score from rules (0.5)
   - +0.2 product match
   - +0.1 state match
   - +0.1 age band match
   - +0.1 smoker tolerance
   - +0.2 health tolerance (capped)
   - +0.3 retrieval similarity

4. **Optional LLM Enhancement** (if `ENABLE_OPENAI_SCORING=true`):
   - Summarize top retrieved chunks
   - Get GPT-4 confidence score and reason
   - Blend with rule-based score

### Knowledge Base

The system indexes carrier product documents (PDFs, HTML) and uses them to:
- Augment rule-based eligibility checks
- Provide evidence for recommendations
- Stay current without code changes

**Supported formats:**
- `.pdf` (via pypdf)
- `.html`, `.htm` (via trafilatura)
- `.txt` (plain text)

Documents are chunked (~800 tokens) and embedded using `all-MiniLM-L6-v2`.

## Troubleshooting

### "No recommendations found"

- Check that knowledge base is indexed: `python scripts/update_kb.py --path data/carriers`
- Verify `config/carriers.yaml` has entries for client's state
- Review logs for eligibility failures

### FAISS index errors

- Delete `data/index/` and rebuild: `python scripts/update_kb.py --path data/carriers --rebuild`
- Ensure sentence-transformers model downloaded: check `~/.cache/huggingface`

### Slow first request

- First request downloads embedding model (~80MB)
- Subsequent requests are fast (~200ms)

## Extending

### Add New Carrier

1. Add carrier config to `config/carriers.yaml`
2. Add portal URL to `config/portal_links.json`
3. Place carrier product PDFs in `data/carriers/`
4. Rebuild index: `python scripts/update_kb.py --path data/carriers`

### Custom Scoring Logic

Edit `src/services/scorer.py` → `score_candidate()` method.

### Additional Health Conditions

Extend `health_tolerance` arrays in `config/carriers.yaml`.

## License

Proprietary - Internal use only
