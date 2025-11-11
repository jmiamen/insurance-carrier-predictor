# Quick Start Guide

Get the Carrier Predictor API running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- 4GB RAM minimum
- 2GB disk space for models

## Installation

### Option 1: Automated Setup (Recommended)

```bash
cd carrier-predictor
bash setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create `.env` file
- Set up data directories

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Create data directories
mkdir -p data/carriers data/index
```

## Build Knowledge Base

The project includes sample carrier documents. Build the index:

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Build index from sample data
python scripts/update_kb.py --path data/carriers
```

**Expected output:**
```
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Loaded 2 files with X chunks
Building FAISS index...
✓ Knowledge base updated successfully!
```

**First run note:** The first time you run this, it will download the embedding model (~80MB). This is a one-time download.

## Start the Server

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Loading existing FAISS index...
INFO:     Loaded FAISS index with X vectors
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Test the API

### 1. Check Health

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "carrier-predictor",
  "version": "1.0.0"
}
```

### 2. Get Recommendations

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
      "product": "Living Promise",
      "confidence": 0.91,
      "reason": "Accepts diabetes; TX eligible; age band 45–85",
      "portal_url": "https://sales.mutualofomaha.com/agent/login"
    },
    {
      "carrier": "Elco Mutual",
      "product": "Golden Eagle",
      "confidence": 0.88,
      "reason": "Diabetes tolerance and TX eligibility",
      "portal_url": "https://elcomutual.com/agent-portal"
    }
  ]
}
```

### 3. Interactive API Docs

Open in your browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Run Tests

```bash
pytest tests/ -v
```

**Expected output:**
```
tests/test_predict.py::test_health_endpoint PASSED
tests/test_predict.py::test_recommend_carriers_success PASSED
tests/test_rules.py::test_rules_load PASSED
tests/test_retriever.py::test_build_query PASSED
...
```

## Adding Your Own Carrier Data

1. **Place documents** in `data/carriers/`:
   - Supported formats: `.pdf`, `.html`, `.txt`
   - Example: `data/carriers/foresters_plan_overview.pdf`

2. **Rebuild the index:**
   ```bash
   python scripts/update_kb.py --path data/carriers --rebuild
   ```

3. **(Optional) Update rules** in `src/config/carriers.yaml`:
   ```yaml
   YourCarrier:
     states: ["TX", "CA", "NY"]
     portal_url: "https://yourcarrier.com/agents"
     products:
       ProductName:
         type: "Whole Life"
         min_age: 18
         max_age: 80
         smoker: true
         health_tolerance: ["diabetes controlled"]
   ```

4. **(Optional) Add portal link** in `src/config/portal_links.json`:
   ```json
   {
     "YourCarrier": "https://yourcarrier.com/agents"
   }
   ```

## Common Issues

### Issue: "No existing index found"
**Solution:** Run `python scripts/update_kb.py --path data/carriers`

### Issue: "No recommendations found"
**Solution:**
- Check that your state is in `src/config/carriers.yaml`
- Ensure knowledge base has relevant documents
- Try a different coverage type or age

### Issue: "Module not found" errors
**Solution:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Issue: Slow first request
**Solution:** This is normal. The embedding model loads on first request (~2-3 seconds). Subsequent requests are fast.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Check the [Dockerfile](Dockerfile) for deployment options
- Review [tests/](tests/) for usage examples

## Support

For issues or questions:
- Check the [README.md](README.md)
- Review logs for error details
- Ensure all dependencies are installed

---

**Ready to go!** 🚀

Your API is running at http://localhost:8000
