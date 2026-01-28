from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import logging
from typing import List, Optional
import os

app = FastAPI(title="UCP Recipe Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UCP_SERVERS = [
    {"url": "http://localhost:8182", "name": "Budget Mart"},
    {"url": "http://localhost:8183", "name": "Premium Grocers"}
]

class ShopRequest(BaseModel):
    recipe: str

class Product(BaseModel):
    id: str
    title: str
    price: int
    image_url: Optional[str] = None
    source: str = "UCP Store"

class ShopResponse(BaseModel):
    items_found: List[Product]
    missing_items: List[str]
    total_cost: int

@app.post("/api/shop", response_model=ShopResponse)
async def shop_for_recipe(request: ShopRequest):
    logger.info(f"Received recipe: {request.recipe}")
    
    # 1. Parse Recipe (Mock NLP)
    raw_items = request.recipe.lower().replace(" and ", ",").replace("\n", ",").split(",")
    ingredients = [item.strip() for item in raw_items if item.strip()]
    logger.info(f"Parsed ingredients: {ingredients}")

    found_products = []
    missing_products = []
    total_cost = 0

    async with httpx.AsyncClient() as client:
        for ingredient in ingredients:
            logger.info(f"Searching for: {ingredient}")
            best_match = None
            
            # Query all stores
            for server in UCP_SERVERS:
                try:
                    response = await client.get(f"{server['url']}/products/search", params={"q": ingredient})
                    if response.status_code == 200:
                        products = response.json()
                        if products:
                            # In real logic, we'd handle multiple matches. Here we take the first.
                            product_data = products[0]
                            # Compare price
                            if best_match is None or product_data["price"] < best_match["price"]:
                                best_match = product_data
                                best_match["source_name"] = server["name"]
                except Exception as e:
                    logger.error(f"Error querying {server['name']}: {e}")

            if best_match:
                p = Product(
                    id=best_match["id"],
                    title=best_match["title"],
                    price=best_match["price"],
                    image_url=best_match.get("image_url"),
                    source=best_match["source_name"]
                )
                found_products.append(p)
                total_cost += p.price
            else:
                missing_products.append(ingredient)

    return ShopResponse(
        items_found=found_products,
        missing_items=missing_products,
        total_cost=total_cost
    )

# Serve Frontend Static Files (Must be after API routes so /api isn't overwritten)
# We assume 'frontend' folder is in the project root (../frontend relative to this file's execution context if run from root)
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
elif os.path.exists("../frontend"):
     app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
