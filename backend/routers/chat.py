"""Chat router - handles conversations"""
import uuid
import time
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from models import ChatRequest, ChatResponse
from services.llm import get_llm_service
from services.products import ProductService
from services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

router = APIRouter()

# Store conversations in memory (in production, use database)
conversations = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Send a message to the guitar store chatbot.

    The chatbot:
    1. Searches the product database for relevant items
    2. Builds a context-aware prompt with product information
    3. Sends it to the LLM (vLLM + Llama)
    4. Returns the generated response
    """

    # Generate conversation ID if not provided
    if not request.conversation_id:
        request.conversation_id = f"conv_{uuid.uuid4()}"

    # Initialize conversation if needed
    if request.conversation_id not in conversations:
        conversations[request.conversation_id] = []

    start_time = time.time()
    sources = []

    try:
        # Step 1: Retrieve relevant products from database
        logger.info(f"Searching products for: {request.message}")
        products = ProductService.search(request.message, limit=5)
        sources.append("products_db")

        if not products:
            logger.info("No specific products found, searching all inventory")
            products = ProductService.get_in_stock()[:3]

        # Step 2: Build prompt with product context
        prompt = PromptBuilder.build_chat_prompt(request.message, products)
        logger.debug(f"Built prompt: {prompt[:200]}...")

        # Step 3: Get LLM service and check availability
        llm_service = get_llm_service()
        is_available = await llm_service.is_available()

        if not is_available:
            logger.error("vLLM server not available")
            # Fallback response if vLLM is not available
            response_text = (
                "I'm sorry, I'm currently unable to process your request. "
                "Please make sure the vLLM server is running on http://localhost:8000"
            )
        else:
            # Step 4: Generate response from LLM
            logger.info("Sending to vLLM for generation...")
            response_text = await llm_service.generate(
                prompt, max_tokens=150, temperature=0.7
            )

            if not response_text:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate response from LLM",
                )

        # Step 5: Add to conversation history
        conversations[request.conversation_id].append(
            {"role": "user", "content": request.message}
        )
        conversations[request.conversation_id].append(
            {"role": "assistant", "content": response_text}
        )

        elapsed_time = time.time() - start_time

        # Build response
        return ChatResponse(
            response=response_text,
            conversation_id=request.conversation_id,
            sources=sources if request.include_sources else [],
            metadata={
                "model": "llama-2-7b",
                "tokens_generated": len(response_text.split()),
                "latency_ms": int(elapsed_time * 1000),
            },
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Retrieve conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id],
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")
