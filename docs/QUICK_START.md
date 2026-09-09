# Quick Start Guide

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **GPU with CUDA support** (recommended for vLLM)
  - If you don't have a GPU, you can still run locally but responses will be slower

## 🚀 Step-by-Step Setup

### 1. Clone/Download the Project

```bash
cd /Users/ocorriga/Learning/guitar_bot
```

### 2. Install vLLM (One-time setup)

```bash
# Install vLLM
pip install vllm torch

# This downloads Llama 2 7B (or your chosen model) - ~15GB
# First run will download and cache the model
```

### 3. Start vLLM Server (Terminal 1)

```bash
# Start the vLLM OpenAI-compatible API server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-hf \
  --port 8000 \
  --gpu-memory-utilization 0.9

# You should see: "Uvicorn running on http://0.0.0.0:8000"
```

**Note:** First startup takes 1-2 minutes as it loads the model into GPU memory.

### 4. Start Backend API (Terminal 2)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8001
```

You should see:

```
Uvicorn running on http://0.0.0.0:8001
```

### 5. Start Frontend (Terminal 3)

```bash
cd frontend
npm install
npm run dev
```

The browser should open automatically at `http://localhost:5173`

## ✅ Verification Checklist

- [ ] vLLM running on port 8000 - check at `http://localhost:8000/health`
- [ ] FastAPI running on port 8001 - check at `http://localhost:8001/health`
- [ ] Frontend running on port 5173 - check at `http://localhost:5173`
- [ ] Status in UI shows "✅ Connected"

## 🎯 Test the Chatbot

Try these questions:

1. **"How much is the Fender Player Stratocaster?"**
   - Should return: €899, 3 in stock

2. **"Do you have any acoustic guitars?"**
   - Should list: Taylor 814ce, Martin D-28

3. **"What's your cheapest guitar?"**
   - Should mention: Ibanez RG550 at €599

4. **"Tell me about Gibson guitars"**
   - Should describe: Gibson Les Paul at €1,299

## 🔧 Troubleshooting

### "Failed to connect to vLLM"

**Problem:** Frontend shows "Backend unavailable"

**Solutions:**
1. Check vLLM is running: `curl http://localhost:8000/health`
2. If not running, start it (see Step 3)
3. Check for GPU memory issues - reduce `--gpu-memory-utilization` to 0.7

### "Connection refused on port 8001"

**Problem:** Can't connect to FastAPI backend

**Solutions:**
1. Check backend is running: `curl http://localhost:8001/health`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check for port conflicts: `lsof -i :8001`

### "CORS errors in browser console"

**Problem:** Frontend can't reach backend

**Solutions:**
1. Make sure backend is running on `http://localhost:8001`
2. Check browser console for the actual error
3. Verify frontend is connecting to the right URL (check `ChatInterface.tsx`)

### "Responses are very slow"

**Problem:** AI generation takes 30+ seconds per response

**Solutions:**
1. **Use a smaller model:**
   ```bash
   python -m vllm.entrypoints.openai.api_server \
     --model meta-llama/Llama-2-7b-hf  # 7B is faster than 13B
   ```

2. **Reduce max tokens:**
   - Edit `backend/services/llm.py` - change `DEFAULT_MAX_TOKENS` to 100

3. **Check GPU usage:**
   ```bash
   nvidia-smi  # Should show GPU utilization
   ```

4. **Enable batching in vLLM:**
   ```bash
   python -m vllm.entrypoints.openai.api_server \
     --model meta-llama/Llama-2-7b-hf \
     --max-model-len 2048
   ```

## 📚 Project Structure

```
guitar_bot/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── models.py              # Request/response schemas
│   ├── routers/
│   │   ├── chat.py            # Chat endpoint
│   │   └── products.py        # Product search API
│   ├── services/
│   │   ├── llm.py             # vLLM client
│   │   ├── products.py        # Guitar database
│   │   └── prompt_builder.py  # Prompt construction
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── InputBox.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
│
└── README.md
```

## 🎓 Understanding the Architecture

### Data Flow

1. **User types message** → React frontend
2. **Frontend sends to backend** → FastAPI at `/api/chat`
3. **Backend**:
   - Searches product database for relevant guitars
   - Builds a prompt with current product info
   - Sends prompt to vLLM
   - Returns AI response
4. **Frontend displays response** → Chat interface

### Why Separate Components?

- **Database (Python dict)** = Facts (prices don't change)
- **vLLM + Llama** = Intelligence (understands natural language)
- **Your backend** = Orchestration (connects everything)
- **React frontend** = User experience (nice chat interface)

### Key Principle

**Don't put business data in the LLM!** Instead, retrieve it from your database and pass it in the prompt. This ensures:
- Always accurate prices and inventory
- Easy to update prices without retraining
- Fast response times
- No hallucinations about products you don't have

## 🚀 Next Steps

1. **Add real database** - Replace `GUITAR_DATABASE` dict with PostgreSQL/MongoDB
2. **Add order placement** - Users can buy through the chat
3. **Add conversation memory** - Remember customer preferences
4. **Deploy to production** - Use Docker + cloud provider

## 📞 Support

Check the main [README.md](../README.md) for API documentation and deployment guides.
