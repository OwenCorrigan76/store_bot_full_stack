# Architecture & Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CUSTOMER                                │
│                  (Web Browser, Mobile)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    "How much is a Strat?"
                             │
                             ▼
            ┌────────────────────────────────┐
            │   React Frontend                │
            │   (Port 5173)                   │
            │                                 │
            │  - Chat UI                      │
            │  - Message history              │
            │  - Status indicator             │
            └──────────┬─────────────────────┘
                       │
                HTTP POST /api/chat
                       │
                       ▼
    ┌────────────────────────────────────────┐
    │     FastAPI Backend (Port 8001)        │
    │                                        │
    │  Router: /api/chat                    │
    │   └─ Extract user message             │
    │                                        │
    │  Services:                            │
    │   ├─ ProductService                  │
    │   ├─ LLMService                      │
    │   └─ PromptBuilder                   │
    └────┬──────────────────────────────┬───┘
         │                              │
         ▼                              ▼
    ┌─────────────┐            ┌──────────────────┐
    │   Guitar    │            │   vLLM Server    │
    │  Database   │            │  (Port 8000)     │
    │  (In-Memory)│            │                  │
    │             │            │ OpenAI API       │
    │ Products:   │            │ Compatible       │
    │ - Fender    │            └────────┬─────────┘
    │ - Gibson    │                     │
    │ - Taylor    │                     ▼
    │ - Ibanez    │            ┌──────────────────┐
    │ - Martin    │            │   Llama Model    │
    │ - PRS       │            │  (GPU Memory)    │
    │             │            │                  │
    │ Each has:   │            │ Llama-2-7B       │
    │ - Price     │            │ or                │
    │ - Stock     │            │ Llama-3.1-8B     │
    │ - Category  │            │                  │
    │ - Tags      │            └──────────────────┘
    └─────────────┘
```

## Request Flow (Detailed)

### Step 1: User Sends Message

```
CUSTOMER:
  "How much is the Fender Player Stratocaster?"
  
        ↓
        
FRONTEND (React)
  - Creates request object
  - Sends HTTP POST to backend
  - Shows loading indicator
  
  Request Body:
  {
    "message": "How much is the Fender Player Stratocaster?",
    "conversation_id": "conv_1234567890",
    "include_sources": true
  }
```

### Step 2: Backend Searches Database

```
BACKEND (FastAPI)
  1. Receives request
  2. Calls ProductService.search()
  
ProductService.search():
  - Split user message into keywords
  - Search guitar database by:
    - Name matching (case-insensitive)
    - Tag matching (e.g., "stratocaster", "fender")
    - Fuzzy string matching
  - Return top 5 matches with scores
  
RESULT:
  [
    Product(
      id="prod_001",
      name="Fender Player Stratocaster",
      price=899,
      currency="EUR",
      stock=3,
      category="electric"
    )
  ]
```

### Step 3: Build Context Prompt

```
BACKEND
  Calls PromptBuilder.build_chat_prompt()
  
SYSTEM PROMPT (Template):
  "You are a helpful guitar store assistant..."
  
PRODUCT CONTEXT (Injected):
  "Relevant products from our inventory:
   
   - Fender Player Stratocaster
     Price: 899 EUR
     In Stock: 3 available
     Category: electric
     Description: Classic Stratocaster with modern playability"

USER MESSAGE:
  "How much is the Fender Player Stratocaster?"

FINAL PROMPT SENT TO LLM:
  [System prompt]
  [Product info]
  [User message]
  "Assistant: "
```

**Key Point:** The LLM never sees the raw database. We curate the information and inject it into the prompt.

### Step 4: LLM Generates Response

```
vLLM Server:
  - Receives prompt
  - Loads Llama model (already in GPU memory)
  - Runs inference
  - Generates tokens one by one:
  
    "The" → "Fender" → "Player" → "Stratocaster" → 
    "is" → "€899" → "and" → "we" → "currently" → 
    "have" → "3" → "in" → "stock" → "." 
    
RESPONSE:
  "The Fender Player Stratocaster is €899, 
   and we currently have 3 in stock."
```

### Step 5: Return to Frontend

```
BACKEND
  Receives response from vLLM
  Builds ChatResponse object:
  {
    "response": "The Fender Player Stratocaster is €899...",
    "conversation_id": "conv_1234567890",
    "sources": ["products_db"],
    "metadata": {
      "model": "llama-2-7b",
      "tokens_generated": 24,
      "latency_ms": 3200
    }
  }
  
        ↓
        
FRONTEND (React)
  Receives HTTP response
  - Hides loading indicator
  - Adds assistant message to chat
  - Auto-scrolls to bottom
  - Shows response to customer
  
CUSTOMER SEES:
  "The Fender Player Stratocaster is €899, 
   and we currently have 3 in stock."
```

## Data Models

### ChatRequest (Frontend → Backend)

```python
{
  "message": str,              # User's question
  "conversation_id": str,      # Optional, for tracking
  "include_sources": bool      # Return data sources used
}
```

### ChatResponse (Backend → Frontend)

```python
{
  "response": str,              # AI-generated answer
  "conversation_id": str,       # Conversation ID
  "sources": list[str],         # ["products_db"]
  "metadata": {
    "model": str,               # "llama-2-7b"
    "tokens_generated": int,    # Number of tokens
    "latency_ms": int          # Response time
  }
}
```

### Product (Internal)

```python
{
  "id": str,                    # "prod_001"
  "name": str,                  # "Fender Player Stratocaster"
  "description": str,           # Product description
  "price": float,               # 899.0
  "currency": str,              # "EUR"
  "stock": int,                 # 3
  "category": str,              # "electric", "acoustic"
  "tags": list[str],            # ["stratocaster", "fender"]
  "image_url": str              # Product image URL
}
```

## Scalability Considerations

### Current Architecture (Development)

```
Single Machine:
┌─────────────────────────────────────────┐
│ vLLM (GPU)                              │
│ + FastAPI (CPU)                         │
│ + React Dev Server                      │
│ All on localhost                        │
└─────────────────────────────────────────┘
```

### Production Architecture (Recommended)

```
┌──────────────────┐
│  Load Balancer   │ (Distributes requests)
└────────┬─────────┘
         │
    ┌────┴────┬────────┬──────────┐
    │          │        │          │
    ▼          ▼        ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│FastAPI├──┤Cache ├──┤ Logs │  │Stats │
│Replica│  │Redis │  │ELK   │  │Prom  │
└───┬──┘  └──────┘  └──────┘  └──────┘
    │
    ├─────────────────────────────┐
    │                             │
    ▼                             ▼
┌─────────────────┐      ┌──────────────────┐
│  PostgreSQL     │      │  vLLM Cluster    │
│  (Products,     │      │  (Multiple GPUs) │
│   Inventory)    │      │  Load Balanced   │
└─────────────────┘      └──────────────────┘
    │                             ▲
    └─────────────────┬───────────┘
                      │
              ┌───────▼────────┐
              │  S3 / Storage  │
              │  (Model weights)│
              └────────────────┘
```

## Key Design Principles

### 1. Separation of Concerns

**Database Layer** → Facts only
```python
Guitar = {
  id, name, price, stock, description
}
# Regularly updated, always accurate
```

**LLM Layer** → Language only
```
Llama understands natural language
Generates human-like responses
No business logic needed
```

**Application Layer** → Orchestration
```python
Backend = {
  fetch_products(),
  build_prompt(),
  call_llm(),
  format_response()
}
# Connects everything together
```

### 2. Context Injection

```
DON'T:
  Tell LLM: "You know the Fender Strat costs $899"
  (What if we change the price tomorrow?)

DO:
  1. Look up price in database
  2. Say: "Here's the current price: €899"
  3. Include in prompt context
  4. LLM uses that context to answer
```

### 3. Stateless Backend

```
Each request is independent
No session state needed
Easy to scale horizontally
```

## Performance Optimizations

### 1. Response Caching

```python
# Cache frequently asked questions
@cache(ttl=3600)  # 1 hour
def search_products(query: str):
    return ProductService.search(query)
```

### 2. Batch Processing

```python
# Send multiple customer requests to vLLM together
# Reduces latency significantly
requests = [
  "What's your cheapest guitar?",
  "Do you have Gibsons?",
  "What about acoustic guitars?"
]
responses = llm.batch_generate(requests)
```

### 3. Token Optimization

```python
# Shorter prompts = faster responses
# Use templates instead of verbose instructions

GOOD:
  "Product: Fender Strat\nPrice: €899\nStock: 3"

BAD:
  "Here is some detailed information about
   one of our finest guitars, the wonderful
   Fender Stratocaster, which is a very
   popular choice among guitarists..."
```

## Security Considerations

### 1. Input Validation

```python
# Sanitize user messages
message = sanitize_input(request.message)
# Prevent prompt injection attacks
```

### 2. Rate Limiting

```python
# Prevent abuse
@ratelimit(max_requests=100, window=60)  # 100 req/min
async def chat(request: ChatRequest):
    ...
```

### 3. Authentication

```
For production:
- Add JWT tokens
- Verify conversation ownership
- Log all requests
```

## Technology Choices

| Component | Choice | Why |
|-----------|--------|-----|
| LLM | Llama 2 7B | Open source, efficient, good quality |
| Inference | vLLM | Fast, OpenAI-compatible API |
| Backend | FastAPI | Modern, fast, easy to use |
| Frontend | React + TypeScript | Type-safe, responsive |
| Database | PostgreSQL | For production; in-memory dict for dev |
| Caching | Redis | Session caching in production |
| Deployment | Docker | Reproducible environments |

## Monitoring & Logging

### Key Metrics

```
- Average response time
- Tokens per second
- GPU memory usage
- Error rate
- Cache hit ratio
- User satisfaction (thumbs up/down)
```

### Logs to Track

```
INFO: User query received
DEBUG: Products found
DEBUG: Prompt built
INFO: LLM response generated
ERROR: Connection to vLLM failed
WARNING: Response took >5 seconds
```
