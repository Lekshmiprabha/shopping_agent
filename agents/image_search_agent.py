"""
agents/image_search_agent.py
─────────────────────────────
Uses Claude Vision to identify a product from an uploaded image or URL,
then searches the store using the existing vector store.
"""
import os, sys, base64
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
import anthropic
from sqlalchemy import func
from db.database import SessionLocal
from db.models import Product, Review
from vector_store.embeddings import search_products
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, TOP_K_RESULTS


def _avg_ratings(db, product_ids: list[int]) -> dict[int, dict]:
    rows = (
        db.query(
            Review.product_id,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .filter(Review.product_id.in_(product_ids))
        .group_by(Review.product_id)
        .all()
    )
    return {
        r.product_id: {
            "avg_rating":   round(r.avg_rating, 1),
            "review_count": r.review_count,
        }
        for r in rows
    }


def _image_to_base64(image_bytes: bytes) -> str:
    return base64.standard_b64encode(image_bytes).decode("utf-8")


def _identify_product_with_claude(
    image_data: str,
    media_type: str,
    source_type: str = "base64",
    image_url: str = "",
) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    if source_type == "url":
        image_block = {
            "type": "image",
            "source": {"type": "url", "url": image_url},
        }
    else:
        image_block = {
            "type": "image",
            "source": {
                "type":       "base64",
                "media_type": media_type,
                "data":       image_data,
            },
        }

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    image_block,
                    {
                        "type": "text",
                        "text": (
                            "You are a product identification assistant for a health-food grocery store. "
                            "Look at this image and decide if it shows a grocery or food product "
                            "(e.g. honey, coffee, nuts, seeds, oil, tea, snacks, grains, dairy alternatives). "
                            "If it IS a grocery/food product, reply with ONLY a short search query "
                            "(3-6 words max), e.g. 'organic raw honey', 'dark roast coffee beans'. "
                            "If it is NOT a grocery product (animals, people, places, vehicles, etc.), "
                            "reply with exactly: NOT_A_PRODUCT "
                            "No explanations, no punctuation, just the query or NOT_A_PRODUCT."
                        ),
                    },
                ],
            }
        ],
    )

    query = response.content[0].text.strip().strip(".,;:")
    logger.info(f"[ImageSearchAgent] Claude identified: '{query}'")
    return query


def run(
    image_bytes: bytes | None = None,
    media_type: str = "image/jpeg",
    image_url: str = "",
    top_k: int = TOP_K_RESULTS,
) -> dict:
    if not image_bytes and not image_url:
        return {"found": False, "identified_query": "",
                "results": [], "message": "No image provided."}

    try:
        if image_bytes:
            b64 = _image_to_base64(image_bytes)
            identified_query = _identify_product_with_claude(b64, media_type, source_type="base64")
        else:
            identified_query = _identify_product_with_claude(
                image_data="", media_type="", source_type="url", image_url=image_url
            )
    except Exception as e:
        logger.error(f"[ImageSearchAgent] Vision error: {e}")
        return {"found": False, "identified_query": "",
                "results": [], "message": f"Could not analyse image: {e}"}

    if not identified_query or identified_query.upper() == "NOT_A_PRODUCT":
        return {
            "found": False, "identified_query": "",
            "results": [],
            "message": "⚠️ No grocery product detected in this image. Please upload a photo of a food or grocery item (e.g. honey, coffee, nuts, seeds).",
        }

    hits = search_products(identified_query, top_k=top_k)
    if not hits:
        return {
            "found": False,
            "identified_query": identified_query,
            "results": [],
            "message": f"🔍 We identified **'{identified_query}'** from your image, but it's not currently available in our store.",
        }

    db = SessionLocal()
    try:
        product_ids = [int(h["id"]) for h in hits]
        db_products = {
            p.id: p
            for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
        }
        ratings = _avg_ratings(db, product_ids)
    finally:
        db.close()

    enriched = []
    for hit in hits:
        pid    = int(hit["id"])
        db_row = db_products.get(pid)
        if db_row is None:
            continue
        r = ratings.get(pid, {"avg_rating": None, "review_count": 0})
        enriched.append({
            **db_row.to_dict(),
            "avg_rating":      r["avg_rating"],
            "review_count":    r["review_count"],
            "relevance_score": hit["relevance_score"],
        })

    enriched.sort(key=lambda p: -p["relevance_score"])

    return {
        "found":            True,
        "identified_query": identified_query,
        "results":          enriched,
        "message":          f"Found **{len(enriched)}** product(s) matching **'{identified_query}'** (identified from your image).",
    }
