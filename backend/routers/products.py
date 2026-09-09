"""Products router - for searching and listing guitars"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models import Product, ProductSearchResponse
from services.products import ProductService

router = APIRouter()


@router.get("/products", response_model=ProductSearchResponse)
async def search_products(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Max results"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    Search for guitars in the inventory.

    This endpoint is used by the backend to find relevant products
    when answering customer questions.
    """
    results = ProductService.search(query, limit=limit, category=category)

    return ProductSearchResponse(
        results=results,
        total=len(results),
        query=query,
    )


@router.get("/products/all")
async def list_all_products(limit: int = Query(100, ge=1, le=500)):
    """List all products in inventory"""
    products = ProductService.list_all(limit=limit)
    return {"products": products, "total": len(products)}


@router.get("/products/stock")
async def get_in_stock():
    """Get all products currently in stock"""
    products = ProductService.get_in_stock()
    return {"products": products, "total": len(products)}


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    product = ProductService.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
