from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Chat Models
class ChatMessage(BaseModel):
    """A message in the conversation"""

    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request to send a message to the chatbot"""

    message: str = Field(..., description="User's question")
    conversation_id: Optional[str] = Field(
        None, description="Conversation ID for tracking"
    )
    include_sources: bool = Field(
        True, description="Include product sources in response"
    )


class ChatResponse(BaseModel):
    """Response from the chatbot"""

    response: str = Field(..., description="AI-generated response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    metadata: dict = Field(
        default_factory=dict, description="Model metadata (tokens, latency, etc.)"
    )


# Product Models
class Product(BaseModel):
    """A guitar product"""

    id: str = Field(..., description="Unique product ID")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., description="Price in currency")
    currency: str = Field(default="EUR", description="Currency code")
    stock: int = Field(..., description="Number in stock")
    category: str = Field(..., description="Product category (e.g., 'electric')")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    image_url: Optional[str] = Field(None, description="Product image URL")


class ProductSearchRequest(BaseModel):
    """Request to search for products"""

    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Max results to return")
    category: Optional[str] = Field(None, description="Filter by category")


class ProductSearchResponse(BaseModel):
    """Response with product search results"""

    results: List[Product] = Field(..., description="Search results")
    total: int = Field(..., description="Total matches found")
    query: str = Field(..., description="Original query")
