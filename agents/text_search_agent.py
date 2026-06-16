"""
Text Search Agent
─────────────────
Searches store.db products by natural language query.
Enriches results with avg rating from the reviews table.
Never invents products not in the database and never returns products that don't match the query.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from sqlalchemy import func
from db.database import SessionLocal
from db.models import Product, Review
from vector_store.embeddings import search_products
from config.settings import TOP_K_RESULTS


def _avg_ratings(db, product_ids: list[int]) -> dict[int, dict]:
    """Return avg rating and review count keyed by product_id."""
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


def run(query: str, top_k: int = TOP_K_RESULTS) -> dict:
    """
    Returns
    -------
    {
        "found":   bool,
        "query":   str,
        "results": list[dict],
        "message": str,
    }
    """
    if not query or not query.strip():
        return {"found": False, "query": query, "results": [],
                "message": "Please enter a search term."}

    logger.info(f"[TextSearchAgent] query='{query}'")
    hits = search_products(query.strip(), top_k=top_k)

    if not hits:
        return {
            "found":   False,
            "query":   query,
            "results": [],
            "message": (
                f"Sorry, we couldn't find any products matching **'{query}'** "
                "in our store. Please try a different search term."
            ),
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

    if not enriched:
        return {"found": False, "query": query, "results": [],
                "message": f"No products found for **'{query}'**."}

    enriched.sort(key=lambda p: -p["relevance_score"])
    logger.info(f"[TextSearchAgent] Returning {len(enriched)} results.")
    return {
        "found":   True,
        "query":   query,
        "results": enriched,
        "message": f"Found {len(enriched)} product(s) matching **'{query}'**.",
    }
