"""Product database and retrieval service"""
from typing import List, Optional
from models import Product
import difflib


# Mock guitar database
GUITAR_DATABASE = [
    Product(
        id="prod_001",
        name="Fender Player Stratocaster",
        description="Classic Stratocaster with modern playability",
        price=899,
        currency="EUR",
        stock=3,
        category="electric",
        tags=["stratocaster", "fender", "electric", "popular"],
        image_url="https://example.com/fender-strat.jpg",
    ),
    Product(
        id="prod_002",
        name="Gibson Les Paul",
        description="Premium semi-hollow body electric guitar",
        price=1299,
        currency="EUR",
        stock=2,
        category="electric",
        tags=["les-paul", "gibson", "electric", "premium"],
        image_url="https://example.com/gibson-lp.jpg",
    ),
    Product(
        id="prod_003",
        name="Taylor 814ce",
        description="High-end acoustic guitar with electronics",
        price=2299,
        currency="EUR",
        stock=1,
        category="acoustic",
        tags=["taylor", "acoustic", "premium", "electronics"],
        image_url="https://example.com/taylor-814.jpg",
    ),
    Product(
        id="prod_004",
        name="Ibanez RG550",
        description="Fast-playing electric guitar perfect for metal",
        price=599,
        currency="EUR",
        stock=5,
        category="electric",
        tags=["ibanez", "electric", "metal", "shredding"],
        image_url="https://example.com/ibanez-rg.jpg",
    ),
    Product(
        id="prod_005",
        name="Martin D-28",
        description="Classic dreadnought acoustic guitar",
        price=1899,
        currency="EUR",
        stock=2,
        category="acoustic",
        tags=["martin", "acoustic", "dreadnought", "classic"],
        image_url="https://example.com/martin-d28.jpg",
    ),
    Product(
        id="prod_006",
        name="PRS Custom 24",
        description="Versatile electric guitar with beautiful finish",
        price=1599,
        currency="EUR",
        stock=1,
        category="electric",
        tags=["prs", "electric", "premium", "versatile"],
        image_url="https://example.com/prs-custom.jpg",
    ),
]


class ProductService:
    """Service for searching and retrieving products"""

    @staticmethod
    def search(query: str, limit: int = 10, category: Optional[str] = None) -> List[Product]:
        """
        Search for products by name, description, or tags.
        Uses fuzzy matching for better results.
        """
        query_lower = query.lower()
        results = []

        for product in GUITAR_DATABASE:
            # Filter by category if provided
            if category and product.category.lower() != category.lower():
                continue

            # Calculate match score
            score = 0

            # Exact name match (highest priority)
            if query_lower in product.name.lower():
                score += 100

            # Tag match
            if any(query_lower in tag for tag in product.tags):
                score += 50

            # Description match
            if query_lower in product.description.lower():
                score += 25

            # Fuzzy match on name
            name_ratio = difflib.SequenceMatcher(
                None, query_lower, product.name.lower()
            ).ratio()
            score += int(name_ratio * 20)

            if score > 0:
                results.append((product, score))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)

        # Return only products (not scores), limited
        return [product for product, _ in results[:limit]]

    @staticmethod
    def get_by_id(product_id: str) -> Optional[Product]:
        """Retrieve a product by ID"""
        for product in GUITAR_DATABASE:
            if product.id == product_id:
                return product
        return None

    @staticmethod
    def list_all(limit: int = 100) -> List[Product]:
        """List all products"""
        return GUITAR_DATABASE[:limit]

    @staticmethod
    def get_in_stock() -> List[Product]:
        """Get all products currently in stock"""
        return [p for p in GUITAR_DATABASE if p.stock > 0]

    @staticmethod
    def format_product_info(product: Product) -> str:
        """Format product information for inclusion in prompts"""
        return f"""
Product: {product.name}
Price: {product.price} {product.currency}
Stock: {product.stock} available
Description: {product.description}
Category: {product.category}
"""
