# AI Customer Support System

An intelligent customer support chatbot powered by **RAG (Retrieval Augmented Generation)** with real e-commerce dataset.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-purple)
![Groq](https://img.shields.io/badge/Groq-LLM-orange)

---

## 🎯 What This Project Does

1. **User asks a question** → "How do I return an item?"
2. **RAG searches** → Finds relevant answers from 100 Q&A knowledge base
3. **LLM generates response** → Natural, helpful answer using context
4. **Escalation option** → Connects to human support via email (n8n + Gmail)

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   FastAPI   │────▶│  Pinecone   │
│  (Browser)  │     │  (Backend)  │     │ (100 vectors)│
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │HuggingFace│ │   Groq   │ │   n8n    │
        │(Embedding)│ │  (LLM)   │ │ (Email)  │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI (Python) | API server |
| **Vector Database** | Pinecone | Store & search embeddings |
| **Embeddings** | HuggingFace API | Convert text to vectors |
| **LLM** | Groq (Llama 3.3 70B) | Generate responses |
| **Automation** | n8n | Email escalation |
| **Frontend** | HTML/CSS/JavaScript | Chat interface |

---

## 📊 Dataset

**100 real e-commerce customer support Q&As** covering:

| Category | Examples |
|----------|----------|
| Shipping | Delivery times, tracking, international |
| Returns | Return policy, refunds, exchanges |
| Payment | Methods, security, payment plans |
| Products | Laptops, phones, headphones, TVs, gaming |
| Account | Login, password reset, settings |
| Tech Support | Troubleshooting, app issues |
| Warranty | Coverage, claims, extensions |

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.10+
- Free accounts: Pinecone, Groq, HuggingFace, n8n

---

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-customer-support.git
cd ai-customer-support
```

---

### Step 2: Get Free API Keys

| Service | URL | What to Get |
|---------|-----|-------------|
| **Pinecone** | [app.pinecone.io](https://app.pinecone.io) | API Key |
| **Groq** | [console.groq.com](https://console.groq.com) | API Key |
| **HuggingFace** | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | Access Token |
| **n8n** | [n8n.cloud](https://n8n.cloud) | Webhook URL |

---

### Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 4: Configure Environment

```bash
# Create .env file
copy .env.example .env
```

Edit `.env` with your API keys:

```env
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=customer-support
GROQ_API_KEY=gsk_your-groq-key
HF_TOKEN=hf_your-huggingface-token
N8N_WEBHOOK_URL=https://your-n8n.app.n8n.cloud/webhook/support-escalation
```

---

### Step 5: Load Dataset into Pinecone

```bash
python load_data.py
```

Expected output:
```
🚀 E-Commerce Support Dataset Loader
==================================================
📂 Loading dataset from: ../data/ecommerce_support_dataset.csv
📊 Found 100 records
📤 Embedded: How long does shipping take?...
📤 Embedded: Do you ship internationally?...
...
✅ Upload complete!
📈 Total vectors in Pinecone: 100
🧪 Testing search...
   Query: 'How do I return an item?'
   Found 3 results:
   1. [0.817] How do I return an item?...
✨ Dataset loaded successfully!
```

---

### Step 6: Run Backend

```bash
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ RAG System initialized
INFO:     Application startup complete.
```

---

### Step 7: Run Frontend

Open **new terminal**:

```bash
cd frontend
python -m http.server 3000
```

---

### Step 8: Open Browser

Go to: **http://localhost:3000**

---

## 🧪 Testing

### Test Chat (RAG)

Ask these questions:

| Question | Expected Source |
|----------|-----------------|
| "How do I return an item?" | Returns category |
| "How long does shipping take?" | Shipping category |
| "What laptops do you recommend?" | Laptop category |
| "What payment methods do you accept?" | Payment category |

### Test Escalation (n8n)

1. Type: "I want to talk to a human"
2. Fill in email form
3. Check your inbox for confirmation email

---

## 📁 Project Structure

```
ai-customer-support/
├── backend/
│   ├── main.py              # FastAPI endpoints
│   ├── rag_system.py        # RAG logic (search + generate)
│   ├── config.py            # Environment settings
│   ├── load_data.py         # CSV → Pinecone loader
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
├── frontend/
│   └── index.html           # Chat UI
├── data/
│   └── ecommerce_support_dataset.csv
└── README.md
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message, get AI response |
| `/api/escalate` | POST | Trigger email escalation |
| `/api/knowledge/add` | POST | Add new document |
| `/api/knowledge/search` | POST | Search knowledge base |
| `/api/stats` | GET | System statistics |
| `/api/categories` | GET | List categories |
| `/health` | GET | Health check |

### Example Chat Request

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I return an item?"}'
```

### Example Response

```json
{
  "response": "To return an item, log into your account, go to Order History, select the item, and print the prepaid shipping label...",
  "session_id": "abc-123",
  "sources": ["How do I return an item?", "What is your return policy?"],
  "needs_escalation": false,
  "confidence_score": 0.85
}
```

---

## 🔄 How RAG Works

```
1. User: "How do I return something?"
              │
              ▼
2. HuggingFace converts to vector
   [0.12, -0.45, 0.78, ...]
              │
              ▼
3. Pinecone finds similar vectors
   → "How do I return an item?" (92% match)
   → "What is your return policy?" (85% match)
              │
              ▼
4. Groq LLM generates response
   using retrieved context
              │
              ▼
5. User receives natural answer
```

---

## 📈 Free Tier Limits

| Service | Free Limit |
|---------|------------|
| Pinecone | 100K vectors, 1 index |
| Groq | 30 requests/min, 6000 tokens/min |
| HuggingFace | Unlimited (rate limited) |
| n8n Cloud | 5 workflows |

---

## 🔧 Customization

### Add Your Own Data

Edit `data/ecommerce_support_dataset.csv`:

```csv
id,category,question,answer,product
101,shipping,"Your question here","Your answer here",general
```

Then reload:
```bash
python load_data.py
```

### Add Single Document via API

```bash
curl -X POST http://localhost:8000/api/knowledge/add \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New FAQ Question",
    "content": "Answer to the question",
    "category": "shipping"
  }'
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Make sure backend is running on port 8000 |
| "No sources found" | Run `python load_data.py` to load data |
| "Rate limit error" | Wait 1 minute (Groq free tier limit) |
| "Escalation not working" | Check n8n workflow is active |

---

## 🎯 Portfolio Highlights

This project demonstrates:

- ✅ **RAG Architecture** - Modern AI pattern
- ✅ **Vector Databases** - Semantic search with Pinecone
- ✅ **LLM Integration** - Groq API for fast inference
- ✅ **API Development** - FastAPI with async Python
- ✅ **Real Dataset** - 100 production-quality Q&As
- ✅ **Automation** - n8n workflow integration

---

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Groq Documentation](https://console.groq.com/docs)
- [RAG Explained](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

# 🚀 Deployment Guide (Optional)

> **Want to deploy this live?** Follow these instructions to host your project for free.

---

## Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │     │    Backend      │     │    Pinecone     │
│    (Vercel)     │────▶│    (Render)     │────▶│   (Cloud DB)    │
│      FREE       │     │      FREE       │     │      FREE       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Step 1: Push Code to GitHub

```bash
cd ai-customer-support

git init
git add .
git commit -m "AI Customer Support System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-customer-support.git
git push -u origin main
```

---

## Step 2: Create Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `backend/.dockerignore`:

```
venv/
__pycache__/
*.pyc
.env
.git/
```

---

## Step 3: Deploy Backend on Render (Free)

1. Go to [render.com](https://render.com) → Sign up with GitHub

2. Click **"New +"** → **"Web Service"**

3. Connect your GitHub repo

4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `ai-support-backend` |
| **Root Directory** | `backend` |
| **Runtime** | `Docker` |
| **Plan** | `Free` |

5. Add **Environment Variables**:

| Key | Value |
|-----|-------|
| `PINECONE_API_KEY` | your-pinecone-key |
| `PINECONE_INDEX_NAME` | customer-support |
| `GROQ_API_KEY` | your-groq-key |
| `HF_TOKEN` | your-huggingface-token |
| `N8N_WEBHOOK_URL` | your-n8n-webhook-url |

6. Click **"Create Web Service"**

7. Wait ~5-10 minutes for deployment

8. Get your URL: `https://ai-support-backend.onrender.com`

---

## Step 4: Update Frontend API URL

Edit `frontend/index.html`, find:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

Change to your Render URL:

```javascript
const API_BASE_URL = 'https://ai-support-backend.onrender.com';
```

Commit and push:

```bash
git add .
git commit -m "Update API URL for production"
git push
```

---

## Step 5: Deploy Frontend on Vercel (Free)

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub

2. Click **"Add New..."** → **"Project"**

3. Import your GitHub repo

4. Configure:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Other` |
| **Root Directory** | `frontend` |

5. Click **"Deploy"**

6. Get your URL: `https://ai-customer-support.vercel.app`

---

## Step 6: Test Live Site

1. Open your Vercel URL
2. Try chatting with the bot
3. Test escalation with your email

---

## ⚠️ Free Tier Limitations

| Service | Limitation |
|---------|------------|
| **Render** | Server sleeps after 15 min inactivity. First request takes ~30s (cold start) |
| **Vercel** | No limitations for static sites |
| **Pinecone** | 100K vectors max |
| **Groq** | 30 requests/min |

### Keep Server Awake (Optional)

Use [UptimeRobot](https://uptimerobot.com) (free) to ping your backend every 14 minutes.

---

## 🎉 Your Live URLs

| Service | URL |
|---------|-----|
| **Frontend** | `https://your-project.vercel.app` |
| **Backend** | `https://ai-support-backend.onrender.com` |
| **API Docs** | `https://ai-support-backend.onrender.com/docs` |

---

# 📄 License

MIT License - Free for personal and commercial use.

---

## 👨‍💻 Author

**Emon**

- GitHub: [your-github](https://github.com/EmonKarmaker)


---

⭐ **Star this repo if you found it helpful!**
