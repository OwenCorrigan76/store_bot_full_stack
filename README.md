# Guitar Store Chatbot

A full-stack application demonstrating an e-commerce chatbot powered by Llama 3.1 8B via vLLM.

## Architecture Overview

```
┌─────────────┐
│   React     │ (Customer chat interface)
│  Frontend   │
└──────┬──────┘
       │ HTTP REST
       ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  - Orchestrates     │
│  - Retrieves data   │
│  - Builds prompts   │
└──────┬──────────────┘
       │ HTTP
       ├─────────────────┬─────────────┐
       ▼                 ▼             ▼
   ┌────────┐    ┌──────────────┐  ┌──────────┐
   │Guitar  │    │ vLLM Server  │  │ Products │
   │Database│    │ (Llama 3.1)  │  │ API      │
   └────────┘    └──────────────┘  └──────────┘
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- GPU with CUDA support (for running vLLM efficiently)

### 1. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start vLLM Server

```bash
# Install vLLM
pip install vllm

# Start vLLM with Llama 3.1 8B
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-hf \
  --port 8000
```

### 3. Start FastAPI Backend

```bash
# From backend directory
uvicorn main:app --reload --port 8001
```

### 4. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

## Project Structure

```
guitar_bot/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── routers/
│   │   ├── chat.py            # Chat endpoint
│   │   └── products.py        # Product retrieval
│   ├── services/
│   │   ├── llm.py             # vLLM client
│   │   ├── products.py        # Product database
│   │   └── prompt_builder.py  # Prompt construction
│   ├── models.py              # Pydantic schemas
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── InputBox.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
└── README.md
```

## Key Concepts

### Data Flow

1. **Customer sends message** → React frontend
2. **Frontend → Backend API** → `/api/chat` endpoint
3. **Backend**:
   - Extracts user intent (e.g., product name)
   - Queries product database
   - Builds context-aware prompt
   - Sends to vLLM
   - Returns AI response
4. **Backend → Frontend** → Display in chat

### Important Principle

**Don't put business data in the LLM.** Instead:
- Keep prices/inventory in a database
- Retrieve relevant data for the current conversation
- Pass retrieved data to the LLM in the prompt
- This way you always have current information

## API Endpoints

### POST `/api/chat`
Send a customer message and get a response.

**Request:**
```json
{
  "message": "How much is the Fender Player Stratocaster?",
  "conversation_id": "conv_123"
}
```

**Response:**
```json
{
  "response": "The Fender Player Stratocaster is €899, and we currently have 3 in stock.",
  "sources": ["products_db"],
  "metadata": {
    "model": "llama-3.1-8b",
    "tokens_generated": 42
  }
}
```

### GET `/api/products`
Search for products.

**Request:**
```
GET /api/products?query=stratocaster&limit=10
```

**Response:**
```json
{
  "results": [
    {
      "id": "prod_001",
      "name": "Fender Player Stratocaster",
      "price": 899,
      "currency": "EUR",
      "stock": 3,
      "category": "electric"
    }
  ]
}
```

## Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## Deployment

See `DEPLOYMENT.md` for production deployment strategies.

## Troubleshooting

### vLLM Connection Errors
- Ensure vLLM server is running on `http://localhost:8000`
- Check GPU memory (Llama 3.1 8B needs ~16GB VRAM)

### Slow Responses
- Reduce `max_tokens` in the prompt
- Use a smaller model (Llama 2 7B instead of 13B)
- Enable batching in vLLM

### CORS Issues
- Backend CORS is configured in `main.py`
- If frontend can't reach backend, check the allowed origins

## Next Steps

- [ ] Connect to real product database
- [ ] Add conversation history/memory
- [ ] Implement order placement through chat
- [ ] Add multilingual support
- [ ] Deploy to production environment
