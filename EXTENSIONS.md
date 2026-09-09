# Extension Guide

How to extend the Guitar Store Chatbot with new features.

## Adding New Features

### 1. Connect to Real Database

Currently using in-memory dictionary. Replace with PostgreSQL:

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/guitar_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# models.py
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    category = Column(String)
```

Replace `ProductService.search()` to query database:

```python
# services/products.py
def search(query: str) -> List[Product]:
    db = SessionLocal()
    return db.query(Product).filter(
        Product.name.ilike(f"%{query}%")
    ).limit(10).all()
```

### 2. Add Order Placement

Allow customers to buy through chat:

```python
# backend/models.py
class Order(BaseModel):
    product_id: str
    quantity: int
    customer_email: str

# backend/routers/orders.py
from fastapi import APIRouter
from models import Order

router = APIRouter()

@router.post("/orders")
async def create_order(order: Order):
    """Customer clicks 'Buy' in the chat"""
    # Save to database
    # Send confirmation email
    # Process payment (Stripe, PayPal)
    return {"order_id": "ORD123", "status": "confirmed"}

# Add to main.py
app.include_router(orders.router, prefix="/api")
```

Update the system prompt:

```python
SYSTEM_PROMPT = """
...
You can help customers place orders.

If a customer shows interest in a guitar, 
suggest they buy it. For example:
"Would you like me to add this to your cart?"

Never suggest buying guitars we don't have in stock.
"""
```

### 3. Add Conversation Memory

Remember customer preferences:

```python
# backend/services/memory.py
from typing import List
from models import ChatMessage

class ConversationMemory:
    def __init__(self, max_messages: int = 10):
        self.messages: List[ChatMessage] = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str):
        self.messages.append(ChatMessage(role=role, content=content))
        # Keep only last N messages to save tokens
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def get_context(self) -> str:
        """Build context from conversation history"""
        context = "Conversation history:\n"
        for msg in self.messages[-5:]:  # Last 5 messages
            context += f"{msg.role}: {msg.content}\n"
        return context
```

Use memory in prompts:

```python
# services/prompt_builder.py
def build_chat_prompt(user_message: str, products: List[Product], memory: ConversationMemory):
    context = memory.get_context()
    products_info = format_products(products)
    
    prompt = f"""{SYSTEM_PROMPT}

{context}

{products_info}

Customer: {user_message}
Assistant: """
    return prompt
```

### 4. Multi-Language Support

Handle conversations in multiple languages:

```python
# backend/services/translator.py
from googletrans import Translator

translator = Translator()

def translate_to_english(text: str, src_lang: str = 'auto') -> str:
    """Translate user message to English"""
    result = translator.translate(text, src_language=src_lang, dest_language='en')
    return result['translatedText']

def translate_to_user_lang(text: str, target_lang: str) -> str:
    """Translate response back to user's language"""
    result = translator.translate(text, dest_language=target_lang)
    return result['translatedText']

# Update chat endpoint
@router.post("/chat")
async def chat(request: ChatRequest):
    user_lang = request.language or 'en'
    
    # Translate user message to English
    user_message_en = translate_to_english(request.message, user_lang)
    
    # Process in English
    products = ProductService.search(user_message_en)
    prompt = PromptBuilder.build_chat_prompt(user_message_en, products)
    response = await llm.generate(prompt)
    
    # Translate response back to user's language
    response_localized = translate_to_user_lang(response, user_lang)
    
    return ChatResponse(response=response_localized)
```

### 5. Analytics & User Feedback

Track what works:

```python
# backend/services/analytics.py
from sqlalchemy import Column, String, DateTime
from datetime import datetime

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True)
    user_message = Column(String)
    ai_response = Column(String)
    user_rating = Column(Integer)  # 1-5 stars
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation_id = Column(String)

# Add feedback endpoint
@router.post("/feedback")
async def submit_feedback(
    conversation_id: str,
    message_index: int,
    rating: int  # 1-5
):
    """User gives thumbs up/down"""
    # Save to database
    # Can be used to train better models
    return {"status": "saved"}
```

Add thumbs up/down buttons to frontend:

```typescript
// frontend/components/MessageList.tsx
{message.role === "assistant" && (
  <div className="feedback-buttons">
    <button onClick={() => submitFeedback(message.id, 5)}>👍</button>
    <button onClick={() => submitFeedback(message.id, 1)}>👎</button>
  </div>
)}
```

### 6. Product Recommendations

Recommend related products:

```python
# backend/services/recommendations.py
def get_recommendations(product_id: str, limit: int = 3) -> List[Product]:
    """Get similar products"""
    product = ProductService.get_by_id(product_id)
    
    # Find products with similar tags/category
    similar = ProductService.search(
        query=product.category,
        limit=limit * 2
    )
    
    # Filter out the original product
    return [p for p in similar if p.id != product_id][:limit]

# Use in prompts
products_info += "\n\nRecommendations if interested:\n"
for product in get_recommendations(product.id):
    products_info += f"- {product.name} ({product.price})\n"
```

### 7. Advanced Intent Recognition

Use a separate model for intent classification:

```python
# backend/services/intent.py
from transformers import pipeline

# Download once on startup
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_intent(message: str) -> str:
    """Classify user intent"""
    candidate_labels = [
        "asking_for_price",
        "asking_for_stock",
        "asking_for_recommendation",
        "asking_for_comparison",
        "asking_for_specs",
        "wanting_to_buy",
        "general_question"
    ]
    
    result = classifier(message, candidate_labels)
    return result['labels'][0]  # Top intent

# Use for better product selection
@router.post("/chat")
async def chat(request: ChatRequest):
    intent = classify_intent(request.message)
    
    if intent == "asking_for_price":
        products = ProductService.search(request.message, limit=3)
    elif intent == "wanting_to_buy":
        products = ProductService.get_in_stock()
    else:
        products = ProductService.search(request.message, limit=5)
    
    # ... rest of chat logic
```

### 8. Add Inventory Management

Track stock changes:

```python
# backend/routers/inventory.py
@router.post("/inventory/update")
async def update_inventory(product_id: str, quantity: int):
    """Admin endpoint to update stock"""
    product = ProductService.get_by_id(product_id)
    product.stock = quantity
    db.commit()
    return {"status": "updated"}

@router.post("/inventory/order")
async def order_from_supplier(product_id: str, quantity: int):
    """Reorder when stock is low"""
    # Integrate with supplier API
    # Track order status
    # Auto-update inventory when arrives
    pass

@router.get("/inventory/low-stock")
async def get_low_stock(threshold: int = 5):
    """Get products below threshold"""
    return db.query(Product).filter(Product.stock < threshold).all()
```

### 9. Image Recognition

Let customers upload guitar photos:

```python
# backend/routers/image.py
from PIL import Image
import os

@router.post("/identify-guitar")
async def identify_guitar(file: UploadFile):
    """Identify guitar from photo"""
    # Save image
    contents = await file.read()
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)
    
    # Use vision model (OpenAI, Claude, etc.)
    description = analyze_image(f"uploads/{file.filename}")
    
    # Search for similar guitars
    products = ProductService.search(description)
    
    return {"products": products, "description": description}
```

### 10. Video Demos

Show product videos in chat:

```typescript
// frontend/components/ChatInterface.tsx
// In AI response, look for product mentions
const extractProducts = (response: string) => {
  // Parse response for product names
  // Return links to videos
  return {
    videos: [
      { name: "Fender Strat", url: "/videos/fender-strat-demo.mp4" }
    ]
  }
}

// Display below chat message
{message.role === "assistant" && videos.length > 0 && (
  <div className="video-section">
    {videos.map(v => <video src={v.url} controls />)}
  </div>
)}
```

## Testing New Features

```python
# backend/tests/test_recommendations.py
import pytest
from services.recommendations import get_recommendations

def test_get_recommendations():
    recommendations = get_recommendations("prod_001", limit=3)
    assert len(recommendations) == 3
    assert all(p.id != "prod_001" for p in recommendations)

# backend/tests/test_intent.py
from services.intent import classify_intent

def test_classify_intent():
    assert classify_intent("How much is the Strat?") == "asking_for_price"
    assert classify_intent("I want to buy a Gibson") == "wanting_to_buy"

# Run tests
# pytest backend/tests/
```

## Performance Tips

### For Faster Responses

1. **Use smaller model**: Llama 2 7B is faster than 13B
2. **Reduce max_tokens**: Set to 100-150 instead of 200+
3. **Enable batching**: Process multiple requests together
4. **Cache results**: Save common questions/answers
5. **Use quantization**: Run model in FP16 or INT8

### For Better Accuracy

1. **More product context**: Include more details in prompt
2. **Few-shot examples**: Show LLM examples of good responses
3. **Fine-tune on domain data**: Train on guitar conversations
4. **Chain of thought**: Ask LLM to think step-by-step
5. **Multi-stage retrieval**: Initial search → re-rank → prompt

## Deployment of New Features

```bash
# 1. Create feature branch
git checkout -b feature/inventory-management

# 2. Implement feature locally
# 3. Test thoroughly
pytest

# 4. Commit and push
git push origin feature/inventory-management

# 5. Create pull request
# 6. Code review
# 7. Merge to main
# 8. Deploy

# For production, use blue-green deployment:
docker build -t guitar-backend:v1.1.0 .
docker tag guitar-backend:v1.1.0 guitar-backend:latest
# Start new version in parallel
# Test it
# Switch traffic when ready
# Keep old version for quick rollback
```
