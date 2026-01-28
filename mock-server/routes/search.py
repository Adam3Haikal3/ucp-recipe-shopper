from fastapi import APIRouter
from sqlalchemy import select
import db
import logging
from typing import List
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

class ProductSchema(BaseModel):
    id: str
    title: str
    price: int
    image_url: str | None = None

@router.get("/products/search", response_model=List[ProductSchema])
async def search_products(q: str):
    logger.info(f"Searching for products matching: {q}")
    async with db.manager.products_session_factory() as session:
        # Simple simple case-insensitive partial match
        # Try pure lowercase match first if ilike is flaky
        result = await session.execute(
            select(db.Product).where(db.Product.title.ilike(f"%{q}%"))
        )
        products = result.scalars().all()
        logger.info(f"Found {len(products)} products for query '{q}'")
        return products
