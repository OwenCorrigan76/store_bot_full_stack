# 📚 Documentation Index

Welcome to the Guitar Store Chatbot! Here's what to read and when.

## 🚀 Getting Started (Start Here!)

1. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** ← Start here
   - What this project is
   - What's included
   - High-level architecture
   - Key concepts explained

2. **[QUICK_START.md](QUICK_START.md)** ← Read this next
   - Step-by-step setup (5 minutes)
   - How to run locally
   - Verify everything works
   - Troubleshooting

## 📖 Learn More

### Understanding the Architecture
- **[ARCHITECTURE.md](ARCHITECTURE.md)** 
  - Detailed system design
  - Data flow diagrams
  - How requests are processed
  - Performance optimization tips
  - Technology choices explained

### API Documentation
- **[README.md](README.md)**
  - API endpoint reference
  - Request/response examples
  - Code structure overview
  - Testing guide

## 🔧 Building and Extending

### Customization
- **[EXTENSIONS.md](EXTENSIONS.md)**
  - Add new features
  - Connect to real database
  - Add order placement
  - Multi-language support
  - Analytics & feedback
  - Recommendations system
  - Many code examples

### Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)**
  - Docker deployment
  - Cloud deployment (AWS, GCP, Azure)
  - Kubernetes setup
  - Performance tuning
  - Security checklist
  - Cost estimation
  - Monitoring & logging

## 📁 Code Structure

### Backend (FastAPI + Python)
```
backend/
├── main.py              # Entry point, FastAPI app setup
├── models.py           # Request/response data structures
├── routers/            # API endpoints
│   ├── chat.py         # Main chat logic (START HERE)
│   └── products.py     # Product search endpoints
└── services/           # Business logic
    ├── llm.py          # vLLM client
    ├── products.py     # Database operations
    └── prompt_builder.py  # Prompt engineering
```

**Key Files to Read:**
1. `routers/chat.py` - Understand the chat flow
2. `services/products.py` - See the database
3. `services/llm.py` - Learn LLM integration
4. `services/prompt_builder.py` - Understand prompts

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── App.tsx                    # Root component
│   ├── components/
│   │   ├── ChatInterface.tsx      # Main chat UI
│   │   ├── MessageList.tsx        # Display messages
│   │   └── InputBox.tsx           # User input
│   └── styles/                    # CSS styling
└── public/
    └── index.html                 # HTML template
```

**Key Files to Read:**
1. `App.tsx` - App structure and setup
2. `components/ChatInterface.tsx` - Main chat logic
3. `components/MessageList.tsx` - Message display
4. `components/InputBox.tsx` - User input handling

## 🎯 Common Tasks

### "I want to get it running right now"
→ Read **QUICK_START.md** (5 minutes)

### "I want to understand how it works"
→ Read **ARCHITECTURE.md** + code comments

### "I want to customize it for my store"
→ Read **EXTENSIONS.md** (database, products, styling)

### "I want to deploy to production"
→ Read **DEPLOYMENT.md** (Docker, cloud, K8s)

### "I want to add a feature"
→ Read **EXTENSIONS.md** (examples & patterns)

### "I'm stuck and need help"
→ See Troubleshooting in **QUICK_START.md**

## 🔑 Key Concepts

### The Main Idea
```
Your Store Database → Extract Relevant Items → Inject into Prompt → LLM Generates Response
```

Why separate the database from the LLM?
- **Database** holds facts (prices, inventory)
- **LLM** understands language (generates human responses)
- **Your backend** connects them together

This way:
- ✅ Prices always accurate
- ✅ Easy to update inventory
- ✅ No hallucinations
- ✅ Scales to any number of products

### The Three Layers
1. **Frontend (React)** - What users see
2. **Backend (FastAPI)** - Business logic & orchestration
3. **LLM (Llama + vLLM)** - AI brains

### The Data Flow
```
User Message → React → FastAPI → 
Database Search → Prompt Building → vLLM/Llama → Response Generation →
Return to React → Display to User
```

## 💡 Learning Path

**Day 1 - Setup & Understanding**
1. Read PROJECT_OVERVIEW.md (15 min)
2. Follow QUICK_START.md (20 min)
3. Get it running locally (20 min)
4. Try the chatbot (10 min)
Total: ~65 minutes

**Day 2 - Dive Into Code**
1. Read ARCHITECTURE.md (30 min)
2. Review backend/routers/chat.py (20 min)
3. Review frontend/src/App.tsx (15 min)
4. Modify some prompts (20 min)
Total: ~85 minutes

**Day 3 - Customize**
1. Read EXTENSIONS.md (30 min)
2. Update product database (20 min)
3. Modify system prompt (15 min)
4. Update frontend styling (20 min)
Total: ~85 minutes

**Day 4 - Deploy**
1. Read DEPLOYMENT.md (40 min)
2. Choose deployment option (10 min)
3. Set up Docker (30 min)
4. Deploy locally (20 min)
Total: ~100 minutes

## 🎬 Quick Commands Reference

```bash
# Get it running (see QUICK_START.md for full details)

# Terminal 1: Start vLLM
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-hf \
  --port 8000

# Terminal 2: Start Backend
cd backend && uvicorn main:app --reload --port 8001

# Terminal 3: Start Frontend
cd frontend && npm run dev

# Docker way
docker-compose up -d
```

## 📞 Support Resources

### Official Docs
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [vLLM Documentation](https://docs.vllm.ai/)
- [React Documentation](https://react.dev/)
- [Llama Models](https://llama.meta.com/)

### Community
- FastAPI: [GitHub Issues](https://github.com/tiangolo/fastapi/issues)
- vLLM: [GitHub Issues](https://github.com/lm-sys/vllm/issues)
- React: [Discord](https://discord.gg/react)

## 🐛 Debugging Tips

### "LLM not responding"
1. Check vLLM is running: `curl http://localhost:8000/health`
2. Check GPU memory: `nvidia-smi`
3. See vLLM logs for errors

### "Backend crashes"
1. Check Python version: `python --version` (needs 3.10+)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check port conflicts: `lsof -i :8001`

### "Frontend can't reach backend"
1. Check backend running: `curl http://localhost:8001/health`
2. Check browser console for CORS errors
3. Verify frontend API URL in `ChatInterface.tsx`

### "Responses are slow"
1. Reduce `max_tokens` in `services/llm.py`
2. Use smaller model (7B instead of 13B)
3. Check GPU utilization: `nvidia-smi`

Full troubleshooting → **QUICK_START.md**

## 📊 Project Stats

- **Backend**: ~250 lines of Python (FastAPI, vLLM, Pydantic)
- **Frontend**: ~300 lines of TypeScript (React, Axios)
- **Services**: ~200 lines (LLM, Products, Prompts)
- **Total Code**: ~750 lines (production-ready)
- **Documentation**: ~2000 lines (comprehensive guides)

## ✅ Checklist: What to Do

- [ ] Read PROJECT_OVERVIEW.md
- [ ] Follow QUICK_START.md
- [ ] Get it running locally
- [ ] Read ARCHITECTURE.md
- [ ] Review code files
- [ ] Customize product database
- [ ] Modify system prompt
- [ ] Try EXTENSIONS examples
- [ ] Read DEPLOYMENT.md
- [ ] Deploy somewhere

## 🎉 You're Ready!

Everything is set up for you to:
1. **Understand** how AI chatbots work
2. **Run** a production-ready system
3. **Customize** for your use case
4. **Extend** with new features
5. **Deploy** to the cloud

Choose where to start:
- **Never built this before?** → QUICK_START.md
- **Want to understand deeply?** → ARCHITECTURE.md
- **Ready to customize?** → EXTENSIONS.md
- **Want to deploy?** → DEPLOYMENT.md

Happy building! 🎸
