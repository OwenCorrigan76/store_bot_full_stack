# 🎸 Guitar Store Chatbot - Visual Guide

## Project Overview at a Glance

```
┌──────────────────────────────────────────────────────────────────────┐
│                   GUITAR STORE CHATBOT STACK                         │
└──────────────────────────────────────────────────────────────────────┘

                            🌐 FRONTEND
                    ┌─────────────────────────────┐
                    │   React + TypeScript        │
                    │   - Chat Interface UI       │
                    │   - Message Display         │
                    │   - Input Box               │
                    │   Port: 5173                │
                    └──────────────┬──────────────┘
                                   │
                         HTTP POST /api/chat
                                   │
                    ┌──────────────▼──────────────┐
                    │   🔧 BACKEND (FastAPI)      │
                    │   - Chat Logic              │
                    │   - Product Search          │
                    │   - Prompt Building         │
                    │   - Error Handling          │
                    │   Port: 8001                │
                    └──┬───────────────────────┬──┘
                       │                       │
              Query DB │                       │ Send Prompt
                       │                       │
      ┌────────────────▼───┐         ┌────────▼──────────────┐
      │ 🗄️ PRODUCTS DB     │         │ 🤖 vLLM SERVER       │
      │ - Fender Strat:    │         │ - Load Llama Model   │
      │   €899, 3 in stock │         │ - Generate text      │
      │ - Gibson LP:       │         │ - Token by token     │
      │   €1299, 2 stock   │         │ Port: 8000           │
      │ - More...          │         │                      │
      └────────────────────┘         │ ┌──────────────────┐ │
                                     │ │ 🧠 LLAMA MODEL   │ │
                                     │ │ Llama 2 7B       │ │
                                     │ │ (on GPU)         │ │
                                     │ └──────────────────┘ │
                                     └─────────────────────┘
```

## Complete File Structure

```
guitar_bot/                          ← You are here
├── 📖 DOCUMENTATION
│   ├── INDEX.md                    ← Navigation guide (read first!)
│   ├── PROJECT_OVERVIEW.md         ← What this is
│   ├── README.md                   ← Full API reference
│   ├── QUICK_START.md              ← Setup in 5 min
│   ├── ARCHITECTURE.md             ← How it works
│   ├── DEPLOYMENT.md               ← Deploy to production
│   └── EXTENSIONS.md               ← Add features
│
├── 🐍 BACKEND (FastAPI + Python)
│   ├── main.py                     ← Entry point, app setup
│   ├── models.py                   ← Data structures (Pydantic)
│   ├── requirements.txt            ← Dependencies
│   ├── Dockerfile                  ← Container definition
│   ├── .env.example                ← Configuration template
│   ├── .gitignore                  ← Git ignore rules
│   │
│   ├── routers/                    ← API endpoints
│   │   ├── chat.py                 ← Chat endpoint (MAIN)
│   │   └── products.py             ← Product search
│   │
│   └── services/                   ← Business logic
│       ├── llm.py                  ← vLLM integration
│       ├── products.py             ← Database operations
│       └── prompt_builder.py       ← Prompt engineering
│
├── ⚛️  FRONTEND (React + TypeScript)
│   ├── package.json                ← Node dependencies
│   ├── vite.config.ts              ← Build configuration
│   ├── tsconfig.json               ← TypeScript config
│   ├── index.html                  ← HTML template
│   ├── Dockerfile.dev              ← Development container
│   ├── .gitignore                  ← Git ignore rules
│   │
│   └── src/                        ← Source code
│       ├── main.tsx                ← Entry point
│       ├── App.tsx                 ← Root component
│       ├── App.css                 ← Main styling
│       ├── index.css               ← Global styles
│       │
│       ├── components/             ← React components
│       │   ├── ChatInterface.tsx   ← Main chat UI (MAIN)
│       │   ├── MessageList.tsx     ← Message display
│       │   └── InputBox.tsx        ← User input
│       │
│       └── styles/                 ← Component styles
│           ├── ChatInterface.css
│           ├── MessageList.css
│           └── InputBox.css
│
├── 🐳 DOCKER & DEPLOYMENT
│   ├── docker-compose.yml          ← Full stack in Docker
│   ├── check_setup.sh              ← Setup verification
│   └── .gitignore                  ← Git ignore rules
│
└── 📋 ROOT CONFIG
    └── .gitignore                  ← Repository setup
```

## Data Flow Diagram

### Step 1: Customer Sends Message
```
                    CUSTOMER
                       │
              "How much is a Strat?"
                       │
                       ▼
                ┌─────────────────┐
                │  React Frontend │ ← Display message
                │   ChatInterface │
                └────────┬────────┘
                         │
                  HTTP POST to backend
                         │
```

### Step 2: Backend Processes Message
```
                ┌──────────────────────────┐
                │    Backend (FastAPI)     │
                │   routers/chat.py        │
                │                          │
                │  1. Receive message      │
                │  2. Search database      │
                │  3. Build prompt         │
                │  4. Call vLLM            │
                │  5. Return response      │
                └──┬──────────────┬────────┘
                   │              │
         ┌─────────▼────┐  ┌──────▼───────────┐
         │ services/    │  │ services/        │
         │ products.py  │  │ llm.py           │
         │              │  │                  │
         │ Search DB:   │  │ Call vLLM API    │
         │ - Query      │  │ - Send prompt    │
         │ - Rank       │  │ - Get response   │
         │ - Return 5   │  │                  │
         └──────────────┘  └──────────────────┘
```

### Step 3: LLM Generates Response
```
        ┌─────────────────────────────────────┐
        │       vLLM Server (Port 8000)       │
        │                                     │
        │  Received Prompt:                  │
        │  ┌──────────────────────────────┐  │
        │  │ System: You are an assistant │  │
        │  │ Products:                    │  │
        │  │ - Fender Strat €899, 3 stock │  │
        │  │ Customer: How much is a Strat? │  │
        │  └──────────────────────────────┘  │
        │                                     │
        │  Load Llama 3.1 8B from GPU         │
        │  Generate tokens one by one:       │
        │  "The" → "Fender" → "Strat"        │
        │  "is" → "€899" → "..."             │
        │                                     │
        │  Return Full Response:              │
        │  "The Fender Strat is €899..."      │
        └────────────┬───────────────────────┘
                     │
```

### Step 4: Display Response
```
                     │
               HTTP Response
                     │
        ┌────────────▼────────────┐
        │   Frontend (React)      │
        │   ChatInterface.tsx     │
        │                         │
        │  Receive response       │
        │  Add to message list    │
        │  Auto-scroll down       │
        │  Remove loading state   │
        └────────────┬────────────┘
                     │
                     ▼
              CUSTOMER SEES:
        "The Fender Strat is €899,
         and we have 3 in stock."
```

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: USER INTERFACE                                         │
│                                                                 │
│  React Components                                              │
│  ├─ App.tsx (main layout)                                      │
│  ├─ ChatInterface.tsx (orchestration)                          │
│  ├─ MessageList.tsx (display)                                  │
│  └─ InputBox.tsx (input)                                       │
│                                                                 │
│  Responsibility: Show chat, send messages, display responses   │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP REST API
┌────────────────────▼────────────────────────────────────────────┐
│ LAYER 2: APPLICATION LOGIC                                      │
│                                                                 │
│  FastAPI Backend                                               │
│  ├─ main.py (setup, routes)                                    │
│  ├─ routers/chat.py (orchestration)                            │
│  └─ routers/products.py (product endpoints)                    │
│                                                                 │
│  Responsibility: Orchestrate everything, handle requests       │
└────────────────────┬────────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
┌─────────▼──────────┐ ┌───────▼──────────┐
│ LAYER 3A: DATA     │ │ LAYER 3B: AI     │
│                    │ │                  │
│ ProductService     │ │ LLMService      │
│ - Search DB        │ │ - vLLM Client   │
│ - Get prices       │ │ - Generate text │
│ - Check stock      │ │ - Token gen     │
│                    │ │                  │
│ Data: [Products]   │ │ Data: Prompts   │
└─────────┬──────────┘ └────────┬────────┘
          │                     │
┌─────────▼──────────┐ ┌───────▼──────────┐
│ DATABASE           │ │ LLM              │
│ (In-memory dict)   │ │ (Llama on GPU)   │
│                    │ │                  │
│ - Name             │ │ - Generates      │
│ - Price            │ │   natural lang   │
│ - Stock            │ │   responses      │
│ - Description      │ │                  │
└────────────────────┘ └────────────────────┘
```

## Request-Response Cycle

```
TIME: 0ms
├─ User types message
│  └─ "How much is the Fender Player Stratocaster?"
│
TIME: 10ms
├─ Message reaches React component
│  └─ ChatInterface component handles it
│
TIME: 20ms
├─ HTTP POST to http://localhost:8001/api/chat
│  Body:
│  {
│    "message": "How much is the Fender Player Stratocaster?",
│    "conversation_id": "conv_123",
│    "include_sources": true
│  }
│
TIME: 50ms
├─ Backend receives request
│  └─ Extracts message from request body
│
TIME: 60ms
├─ ProductService.search()
│  ├─ Parse: "fender" + "stratocaster"
│  ├─ Query database: O(n) search
│  ├─ Match products
│  └─ Return: [Fender Player Stratocaster]
│
TIME: 70ms
├─ PromptBuilder.build_chat_prompt()
│  ├─ Build system message
│  ├─ Format products
│  └─ Return complete prompt
│
TIME: 80ms
├─ LLMService.generate()
│  ├─ HTTP POST to http://localhost:8000/v1/completions
│  ├─ vLLM loads Llama model (already in memory)
│  └─ Wait for response...
│
TIME: 3000ms (first token)
├─ Llama starts generating
│  ├─ Token 1: "The"
│  ├─ Token 2: "Fender"
│  ├─ Token 3: "Player"
│  ...
│  └─ Token 20: "."
│
TIME: 3200ms
├─ Response: "The Fender Player Stratocaster is €899..."
│
TIME: 3210ms
├─ Backend returns ChatResponse
│  {
│    "response": "The Fender Player...",
│    "conversation_id": "conv_123",
│    "sources": ["products_db"],
│    "metadata": { "tokens_generated": 20, "latency_ms": 3200 }
│  }
│
TIME: 3220ms
├─ Frontend receives response
│  ├─ Parse JSON
│  ├─ Add to messages list
│  ├─ Re-render
│  └─ Auto-scroll to bottom
│
TIME: 3225ms
└─ User sees response on screen
   "The Fender Player Stratocaster is €899,
    and we currently have 3 in stock."

Total Time: ~3.2 seconds
```

## Key Integration Points

```
┌──────────────────────────────────────────────────────────────┐
│ Frontend ↔ Backend                                           │
├──────────────────────────────────────────────────────────────┤
│ Endpoint: POST /api/chat                                     │
│ Port: Backend 8001 ← Frontend 5173                          │
│ Request: { message, conversation_id, include_sources }      │
│ Response: { response, sources, metadata, conversation_id }  │
│ Headers: Content-Type: application/json, CORS allowed       │
│ Status Codes: 200 OK, 500 Error                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Backend ↔ vLLM                                               │
├──────────────────────────────────────────────────────────────┤
│ Endpoint: POST /v1/completions                              │
│ Port: vLLM 8000 ← Backend 8001                             │
│ Request: { model, prompt, max_tokens, temperature }         │
│ Response: { choices: [{ text }] }                          │
│ Status Codes: 200 OK, connection errors                    │
└──────────────────────────────────────────────────────────────┘
```

## File Dependency Graph

```
App.tsx (root)
├─ ChatInterface.tsx
│  ├─ MessageList.tsx
│  ├─ InputBox.tsx
│  └─ axios (HTTP requests)
│     └─ api/chat (backend)
│        └─ routers/chat.py
│           ├─ services/products.py
│           ├─ services/llm.py
│           ├─ services/prompt_builder.py
│           └─ models.py

routers/chat.py
├─ models.py (ChatRequest, ChatResponse)
├─ services/products.py
├─ services/llm.py
└─ services/prompt_builder.py

services/llm.py
└─ httpx (HTTP client)
   └─ vLLM API (port 8000)

services/products.py
├─ models.py (Product)
└─ difflib (fuzzy matching)

services/prompt_builder.py
└─ models.py (Product)
```

## Configuration & Ports

```
SERVICE              PORT    STATUS ENDPOINT      NOTES
─────────────────────────────────────────────────────────
React Frontend       5173    http://localhost:5173/
FastAPI Backend      8001    http://localhost:8001/health
vLLM Server         8000    http://localhost:8000/health
PostgreSQL (optional) 5432   localhost:5432
Redis (optional)     6379    localhost:6379
```

## Development vs Production

```
DEVELOPMENT MODE (Local Testing)
─────────────────────────────────────────────────────────
├─ In-memory database (GUITAR_DATABASE dict)
├─ Hot reload enabled (auto-refresh on save)
├─ Debug mode ON (verbose logs)
├─ CORS allowed from localhost
├─ No authentication
├─ Single instance of everything
├─ Faster startup (no validation)
└─ Good for: Learning, developing, testing

PRODUCTION MODE (Live Users)
─────────────────────────────────────────────────────────
├─ PostgreSQL database
├─ Hot reload OFF (stability)
├─ Debug mode OFF (security)
├─ CORS restricted to your domain
├─ JWT/API authentication
├─ Multiple instances (load balanced)
├─ Thorough validation
├─ Good for: Real users, reliability, scale
```

## Technology Stack at a Glance

```
LAYER           TECHNOLOGY    WHY CHOSEN           VERSION
────────────────────────────────────────────────────────────
Frontend        React          Component-based UI   v18+
Frontend        TypeScript     Type safety          v5+
Styling         CSS3           Modern layout        Native
HTTP Client     Axios          Easy requests        v1.6+

Backend         FastAPI        Fast, modern         v0.104+
Backend         Python         Readable, fast       v3.11+
Data Schema     Pydantic       Validation, types    v2.5+
HTTP Client     httpx          Async HTTP           v0.25+

Inference       vLLM           Fast LLM serving     Latest
Model           Llama 2 7B     Open, efficient      Latest
GPU Support     CUDA/cuDNN     GPU acceleration     Latest

Build Tools     Vite           Fast build           v5+
Package Mgr     npm            Node packages        v9+
Task Runner     Uvicorn        Python server        v0.24+
```

---

**Use this visual guide to:**
- Understand the overall architecture
- Navigate the codebase
- See how data flows through the system
- Understand timing and integration points
- Choose which files to focus on

**Next Step:** Read **QUICK_START.md** to get it running!
