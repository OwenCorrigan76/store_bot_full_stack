"""vLLM integration and LLM service"""
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
VLLM_BASE_URL = "http://localhost:8000"
VLLM_MODEL = "meta-llama/Llama-2-7b-hf"  # Can be Llama-3.1-8B if available
DEFAULT_MAX_TOKENS = 200
DEFAULT_TEMPERATURE = 0.7


class LLMService:
    """Service for communicating with vLLM server"""

    def __init__(self, base_url: str = VLLM_BASE_URL, model: str = VLLM_MODEL):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)

    async def is_available(self) -> bool:
        """Check if vLLM server is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"vLLM health check failed: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Optional[str]:
        """
        Generate text using vLLM's OpenAI-compatible API.

        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Generated text or None if request fails
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/completions",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.95,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("choices"):
                        return data["choices"][0]["text"].strip()
                else:
                    logger.error(f"vLLM error: {response.status_code} {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Failed to generate text from vLLM: {e}")
            return None

    async def chat_completion(
        self,
        messages: list,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Optional[str]:
        """
        Generate chat completions using vLLM's chat API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated message content or None if request fails
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.95,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("choices"):
                        return data["choices"][0]["message"]["content"].strip()
                else:
                    logger.error(f"vLLM error: {response.status_code} {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Failed to get chat completion from vLLM: {e}")
            return None

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global LLM service instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
