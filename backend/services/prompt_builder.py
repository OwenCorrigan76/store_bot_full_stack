"""Prompt building and context management"""
from typing import List
from models import Product


SYSTEM_PROMPT = """You are a helpful guitar store assistant for a music equipment retailer. 

Your job is to help customers find guitars and answer questions about our products.

Guidelines:
1. Be friendly and knowledgeable about guitars
2. When asked about prices or stock, use only the product information provided to you
3. If we don't have a product, suggest similar alternatives from our inventory
4. Keep responses concise (2-3 sentences max)
5. Be honest - if we don't have something, say so
6. Encourage customers to ask about other guitars we carry

Available guitar categories: electric, acoustic, bass, classical"""


class PromptBuilder:
    """Build context-aware prompts for the LLM"""

    @staticmethod
    def build_chat_prompt(
        user_message: str, retrieved_products: List[Product]
    ) -> str:
        """
        Build a prompt that includes user message and relevant product context.

        This is the key principle: inject current database information into the prompt
        so the LLM always has accurate, up-to-date facts.
        """

        # Format product information
        products_info = ""
        if retrieved_products:
            products_info = "Relevant products from our inventory:\n\n"
            for product in retrieved_products:
                products_info += f"""
- {product.name}
  Price: {product.price} {product.currency}
  In Stock: {product.stock} available
  Category: {product.category}
  Description: {product.description}
"""
        else:
            products_info = "No specific products match the customer's query, but we have other guitars available."

        # Combine system prompt, products info, and user message
        full_prompt = f"""{SYSTEM_PROMPT}

{products_info}

Customer: {user_message}
Assistant: """
        return full_prompt