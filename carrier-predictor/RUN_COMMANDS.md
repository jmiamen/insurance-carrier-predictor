# Commands to Run Carrier Predictor Locally

## Quick Start (Copy & Paste)

```bash
# 1. Navigate to project directory
cd /Users/josiahmiamen/Desktop/InsuranceToolKit/carrier-predictor

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (uses defaults, works out-of-the-box)
cp .env.example .env

# 5. Build knowledge base from sample data
python scripts/update_kb.py --path data/carriers

# 6. Start the server
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

## Server will be running at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Test the API

### Terminal 1: Keep server running
```bash
uvicorn src.app:app --reload
```

### Terminal 2: Make test requests

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Get Recommendations (Example 1: Diabetes client)
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

#### Get Recommendations (Example 2: Healthy young client)
```bash
curl -X POST http://localhost:8000/recommend-carriers \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "state": "TX",
    "smoker": false,
    "coverage_type": "Term",
    "desired_coverage": 500000,
    "health_conditions": []
  }'
```

#### Get Recommendations (Example 3: Senior with health issues)
```bash
curl -X POST http://localhost:8000/recommend-carriers \
  -H "Content-Type: application/json" \
  -d '{
    "age": 75,
    "state": "TX",
    "smoker": true,
    "coverage_type": "Final Expense",
    "desired_coverage": 15000,
    "health_conditions": ["copd", "high blood pressure"]
  }'
```

#### Check Knowledge Base Status
```bash
curl http://localhost:8000/kb/status
```

## Run Tests

```bash
# Make sure you're in the project directory with venv activated
pytest tests/ -v
```

## Add More Documents and Rebuild Index

```bash
# 1. Add your PDF/HTML files to data/carriers/
cp /path/to/your/carrier_docs/*.pdf data/carriers/

# 2. Rebuild the index
python scripts/update_kb.py --path data/carriers --rebuild

# 3. Restart the server (it will load the new index)
# Press Ctrl+C in Terminal 1, then run:
uvicorn src.app:app --reload
```

## Using the Interactive Docs (Recommended for Testing)

1. Open http://localhost:8000/docs in your browser
2. Click on **POST /recommend-carriers**
3. Click **"Try it out"**
4. Edit the JSON request body
5. Click **"Execute"**
6. See the response below

## Stopping the Server

Press `Ctrl + C` in the terminal where uvicorn is running.

## Deactivate Virtual Environment

```bash
deactivate
```

## Docker Deployment (Optional)

```bash
# Build image
docker build -t carrier-predictor .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  carrier-predictor

# Access at http://localhost:8000
```

## Troubleshooting

### Error: "No existing index found"
```bash
# Build the index
python scripts/update_kb.py --path data/carriers
```

### Error: "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "Port 8000 already in use"
```bash
# Use a different port
uvicorn src.app:app --reload --port 8001
```

### Error: "No recommendations found"
- Check that TX is in your carriers.yaml states list
- Try different coverage types: "Term", "Whole Life", "Final Expense"
- Check logs for eligibility details

## Environment Variables

Edit `.env` to customize:

```bash
# Use OpenAI for enhanced scoring (optional)
OPENAI_API_KEY=sk-your-key-here
ENABLE_OPENAI_SCORING=true

# Change data directories
DOCS_DIR=data/carriers
INDEX_DIR=data/index

# Adjust logging
LOG_LEVEL=DEBUG
```

## Summary of Key Files

- `src/app.py` - FastAPI application
- `src/routers/predict.py` - Recommendation endpoint
- `src/routers/kb.py` - Knowledge base management
- `src/services/scorer.py` - Scoring logic
- `src/services/rules.py` - Eligibility rules
- `src/config/carriers.yaml` - Carrier configuration
- `src/config/portal_links.json` - Portal URLs
- `scripts/update_kb.py` - CLI for rebuilding index
- `tests/` - Test suite

---

**You're all set!** 🎉

The API is production-ready and works out-of-the-box with local embeddings (no API keys required).
