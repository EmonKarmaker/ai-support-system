# AI Customer Support System V2

## 🚀 Pinecone RAG Edition

A production-ready AI customer support chatbot featuring:
- 🧠 **RAG System** with Pinecone vector database
- 📊 **Real Dataset** - 100 e-commerce support Q&As
- ⚡ **Groq LLM** - Llama 3.3 70B for responses
- 🔄 **n8n Automation** - Email escalation
- 🎨 **Modern UI** - Category filtering, sources display

---

## 📦 Tech Stack (All Free Tier)

| Service | Free Tier | Purpose |
|---------|-----------|---------|
| **Pinecone** | 100K vectors, 1 index | Vector database |
| **Groq** | 30 RPM, 6000 TPM | LLM inference |
| **Sentence Transformers** | Unlimited (local) | Embeddings |
| **n8n Cloud** | 5 workflows | Email automation |
| **Render** | 750 hours/month | Hosting |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/JS)                        │
│              - Chat UI with category filter                  │
│              - Quick action buttons                          │
│              - Source attribution display                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  /api/chat  │  │ /api/search │  │/api/escalate│          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          ▼                ▼                │
┌─────────────────────────────────┐        │
│         RAG SYSTEM              │        │
│  ┌───────────┐ ┌──────────────┐ │        │
│  │ Pinecone  │ │ Sentence     │ │        │
│  │ (Vectors) │ │ Transformers │ │        │
│  └───────────┘ └──────────────┘ │        │
│         │                       │        │
│         ▼                       │        │
│  ┌───────────────────────┐      │        │
│  │    Groq API           │      │        │
│  │  (Llama 3.3 70B)      │      │        │
│  └───────────────────────┘      │        │
└─────────────────────────────────┘        │
                                           ▼
                                  ┌─────────────────┐
                                  │      n8n        │
                                  │  (Webhook →     │
                                  │   Gmail)        │
                                  └─────────────────┘
```

---

## 📊 Dataset

The system includes a real e-commerce customer support dataset with 100 Q&A pairs covering:

- **General Support**: Shipping, Returns, Payment, Account, Orders
- **Product Categories**: Laptops, Phones, Headphones, Smartwatches, TVs, Gaming
- **Technical**: Warranty, Tech Support, Subscriptions, Promos

---

## 🔧 Setup Guide

### Step 1: Get API Keys

#### Pinecone (Free)
1. Go to [app.pinecone.io](https://app.pinecone.io)
2. Sign up for free account
3. Go to **API Keys** → Copy your key
4. Save as `PINECONE_API_KEY`

#### Groq (Free)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → Go to **API Keys**
3. Create new key
4. Save as `GROQ_API_KEY`

#### n8n (Already configured from V1)
- Use your existing webhook URL

---

### Step 2: Setup Project

```bash
# Clone/Download project
cd ai-support-system-v2/backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Configure Environment

```bash
# Create .env file
copy .env.example .env

# Edit .env with your keys
notepad .env
```

Fill in:
```env
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=customer-support
GROQ_API_KEY=gsk_your_groq_key
N8N_WEBHOOK_URL=https://your-n8n.app.n8n.cloud/webhook/support-escalation
```

---

### Step 4: Load Dataset into Pinecone

```bash
# This vectorizes the CSV and uploads to Pinecone
python load_data.py
```

You'll see:
```
🚀 E-Commerce Support Dataset Loader
==================================================
📂 Loading dataset from: ../data/ecommerce_support_dataset.csv
📊 Found 100 records
🔄 Uploading 100 documents to Pinecone...
📤 Uploaded batch 1/1
✅ Upload complete!
📈 Total vectors in Pinecone: 100
🧪 Testing search...
   Query: 'How do I return an item?'
   Found 3 results:
   1. [0.847] How do I return an item?...
✨ Dataset loaded successfully!
```

---

### Step 5: Run Backend

```bash
uvicorn main:app --reload --port 8000
```

---

### Step 6: Run Frontend

Open new terminal:
```bash
cd ../frontend
python -m http.server 3000
```

---

### Step 7: Test It!

1. Open browser: `http://localhost:3000`
2. Ask questions like:
   - "How do I return an item?"
   - "What laptops do you recommend?"
   - "How long does shipping take?"
   - "I want to talk to a human"

---

## 📁 Project Structure

```
ai-support-system-v2/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── rag_system.py        # Pinecone RAG logic
│   ├── config.py            # Environment config
│   ├── load_data.py         # Dataset loader script
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment template
├── frontend/
│   └── index.html           # Chat UI
├── data/
│   └── ecommerce_support_dataset.csv  # 100 Q&A pairs
└── README.md
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message, get RAG response |
| `/api/escalate` | POST | Trigger email escalation |
| `/api/knowledge/add` | POST | Add single document |
| `/api/knowledge/search` | POST | Search knowledge base |
| `/api/stats` | GET | Get system statistics |
| `/api/categories` | GET | List available categories |
| `/health` | GET | Health check |

---

## 🎯 Portfolio Highlights

This project demonstrates:

✅ **Vector Databases** - Pinecone for semantic search  
✅ **RAG Architecture** - Context retrieval + LLM generation  
✅ **Real Dataset** - 100 production-quality Q&As  
✅ **Modern Stack** - FastAPI, async Python  
✅ **Automation** - n8n workflow integration  
✅ **Free Tier Deployment** - Cost-effective architecture  

---

## 📈 Extending the Project

### Add More Data
```python
# Via API
curl -X POST http://localhost:8000/api/knowledge/add \
  -H "Content-Type: application/json" \
  -d '{"title": "New Question", "content": "Answer here", "category": "shipping"}'
```

### Add Your Website Content
```python
# Create a scraper or add your own CSV
# Follow the same format: id, category, question, answer, product
```

---

## 📄 License

MIT - Free for personal and commercial use.

---

Built with ❤️ by Emon | Perfect for AI/ML Engineering portfolios!
