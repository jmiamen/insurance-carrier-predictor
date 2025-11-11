# 🚀 Deploy Insurance Carrier Predictor to Render

Complete guide to deploy your medication-based carrier predictor web app to Render.

---

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free tier available)
3. **Git installed** locally

---

## 🎯 Quick Deploy (Recommended)

### Option 1: Deploy with Blueprint (Easiest)

1. **Push code to GitHub:**
   ```bash
   cd /Users/josiahmiamen/Desktop/InsuranceToolKit/carrier-predictor
   git init
   git add .
   git commit -m "Initial commit: Carrier predictor with medication reference"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/carrier-predictor.git
   git push -u origin main
   ```

2. **Deploy to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and deploy both services

3. **Wait for deployment** (~5-10 minutes first time)

4. **Access your app:**
   - Frontend: `https://carrier-predictor-frontend.onrender.com`
   - API: `https://carrier-predictor-api.onrender.com`

---

## 🛠️ Manual Deploy (Alternative)

### Deploy Backend API

1. **Create New Web Service:**
   - Dashboard → "New +" → "Web Service"
   - Connect GitHub repository
   - Configure:
     - **Name:** `carrier-predictor-api`
     - **Region:** Oregon (US West)
     - **Branch:** `main`
     - **Root Directory:** (leave blank)
     - **Runtime:** Python 3
     - **Build Command:**
       ```bash
       pip install --upgrade pip && pip install -r requirements.txt && python scripts/update_kb.py --path data --rebuild
       ```
     - **Start Command:**
       ```bash
       uvicorn src.app:app --host 0.0.0.0 --port $PORT
       ```
     - **Plan:** Free (or Starter for better performance)

2. **Environment Variables:**
   - Click "Advanced" → "Add Environment Variable"
   - Add: `PYTHON_VERSION` = `3.10.0`

3. **Health Check:**
   - Path: `/health`

4. **Deploy** and wait for build to complete

### Deploy Frontend

1. **Create New Static Site:**
   - Dashboard → "New +" → "Static Site"
   - Connect same GitHub repository
   - Configure:
     - **Name:** `carrier-predictor-frontend`
     - **Branch:** `main`
     - **Root Directory:** `frontend`
     - **Build Command:**
       ```bash
       npm install && npm run build
       ```
     - **Publish Directory:** `build`

2. **Environment Variables:**
   - `REACT_APP_API_URL` = Your backend URL (e.g., `https://carrier-predictor-api.onrender.com`)

3. **Deploy**

---

## 🔧 Configuration Details

### Backend Configuration (`requirements.txt`)

Ensure your `requirements.txt` has compatible versions:
```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.6.0
python-dotenv==1.0.1
sentence-transformers>=3.0.0
faiss-cpu==1.9.0
torch>=2.0.0
numpy<2.0
pypdf==5.1.0
trafilatura==1.12.2
pyyaml==6.0.2
```

### Frontend Configuration

Update `frontend/src/App.js` to use environment variable for API URL:

```javascript
// At the top of App.js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// In handleSubmit function
const response = await axios.post(`${API_URL}/recommend-carriers`, payload);
```

---

## 🌐 Production Optimizations

### 1. **Use Persistent Disk for Knowledge Base**

On Render, the FAISS index rebuilds on every deploy. To persist it:

1. Go to your web service
2. "Environment" → "Disk"
3. Add disk:
   - **Mount Path:** `/app/data/index`
   - **Size:** 1GB (Free tier includes 512MB)

### 2. **Enable CORS Properly**

Update `src/app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://carrier-predictor-frontend.onrender.com",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. **Add Custom Domain** (Optional)

1. Go to Settings → "Custom Domain"
2. Add your domain (e.g., `insurancepredictor.com`)
3. Update DNS records as instructed

---

## 🧪 Testing Deployment

### 1. Test Backend API
```bash
curl https://carrier-predictor-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "carrier-predictor",
  "version": "1.0.0"
}
```

### 2. Test Medication Query
```bash
curl -X POST https://carrier-predictor-api.onrender.com/recommend-carriers \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55,
    "state": "TX",
    "gender": "M",
    "smoker": false,
    "coverage_type": "Term",
    "desired_coverage": 250000,
    "medications": ["Metformin", "Lisinopril"]
  }'
```

### 3. Test Frontend
- Visit: `https://carrier-predictor-frontend.onrender.com`
- Enter medications and get recommendations

---

## 📊 Monitoring

### View Logs
1. Dashboard → Your Service → "Logs"
2. Filter by time range
3. Check for errors or slow queries

### Metrics
1. Dashboard → Your Service → "Metrics"
2. Monitor CPU, Memory, Response Time

---

## 🐛 Troubleshooting

### Build Fails

**Error: "No module named 'sentence_transformers'"**
- Solution: Verify `requirements.txt` is in root directory
- Check build command includes `pip install -r requirements.txt`

**Error: "Python version mismatch"**
- Solution: Add environment variable `PYTHON_VERSION=3.10.0`

### Knowledge Base Issues

**Error: "No existing index found"**
- Solution: Ensure build command includes `python scripts/update_kb.py --path data --rebuild`
- Check that `data/carriers/` folder is in your repository

### Frontend Can't Connect to Backend

**Error: "Network Error" in browser console**
- Solution: Update `REACT_APP_API_URL` environment variable
- Verify CORS settings in backend
- Check backend is deployed and healthy

### Slow First Request

**Issue: First API call takes 30+ seconds**
- This is normal on free tier (cold start)
- Solution: Upgrade to Starter plan ($7/month) for always-on instances

---

## 💰 Cost Breakdown

### Free Tier
- ✅ Backend API: Free (with cold starts)
- ✅ Frontend: Free
- ✅ Total: $0/month
- ⚠️ Limitations: Cold starts after 15 min inactivity, 750 hours/month

### Starter Plan (Recommended)
- Backend API: $7/month (always-on, no cold starts)
- Frontend: Free
- Total: $7/month
- Benefits: Faster, more reliable, 400 build minutes

---

## 🔒 Security Best Practices

1. **Environment Variables:**
   - Never commit API keys or secrets
   - Use Render's environment variables feature

2. **CORS:**
   - Restrict to your frontend domain in production
   - Don't use `allow_origins=["*"]` in production

3. **Rate Limiting:**
   - Consider adding rate limiting for production
   - Use Render's built-in DDoS protection

---

## 🚀 Next Steps

After deployment:

1. **Add Custom Domain**
2. **Set up monitoring** (Render + external services)
3. **Enable SSL** (automatic with Render)
4. **Add analytics** (Google Analytics, Plausible, etc.)
5. **Create backup strategy** for knowledge base
6. **Set up CI/CD** for automatic deployments

---

## 📞 Support

- **Render Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev

---

## 🎉 Success!

Your Insurance Carrier Predictor is now live!

**What users can do:**
✅ Enter client age, state, coverage type
✅ Add medications (autocomplete from common list)
✅ Get instant carrier recommendations
✅ See which carriers accept diabetes, BP meds, etc.
✅ Access carrier portals directly

**Powered by:**
- 📚 22 carrier files + medication reference
- 🤖 AI-powered matching with FAISS
- 💊 Medication-to-condition mapping
- 📦 4-box carrier positioning system

---

**Deployment Checklist:**

- [ ] Code pushed to GitHub
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Render
- [ ] Environment variables configured
- [ ] Health check passing
- [ ] Test medication query works
- [ ] Frontend connects to backend
- [ ] Custom domain added (optional)
- [ ] SSL certificate active
- [ ] Monitoring set up

**You're ready to go! 🎊**
