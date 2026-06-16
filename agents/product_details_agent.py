"""
Product Details Agent
──────────────────────
Fetches full product record + all reviews from store.db for a selected product.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from sqlalchemy import func
from db.database import SessionLocal
from db.models import Product, Review


def _stars(rating: float) -> str:
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "½" * half + "☆" * empty + f"  {rating:.1f}/5"


def run(product_id: int) -> dict:
    """
    Returns
    -------
    {
        "found":   bool,
        "product": dict | None,
        "reviews": list[dict],
        "message": str,
    }
    """
    logger.info(f"[ProductDetailsAgent] product_id={product_id}")
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return {"found": False, "product": None, "reviews": [],
                    "message": f"Product with id {product_id} not found."}

        # aggregate rating
        agg = (
            db.query(
                func.avg(Review.rating).label("avg"),
                func.count(Review.id).label("cnt"),
            )
            .filter(Review.product_id == product_id)
            .first()
        )
        avg_rating   = round(agg.avg, 1) if agg.avg else None
        review_count = agg.cnt or 0

        # fetch all reviews for this product
        reviews = [
            r.to_dict()
            for r in db.query(Review)
            .filter(Review.product_id == product_id)
            .order_by(Review.rating.desc())
            .all()
        ]

        detail = product.to_dict()
        detail["avg_rating"]      = avg_rating
        detail["review_count"]    = review_count
        detail["rating_display"]  = _stars(avg_rating) if avg_rating else "No ratings yet"
        detail["organic_label"]   = "🌿 Organic" if product.is_organic else ""

        return {"found": True, "product": detail, "reviews": reviews, "message": ""}
    finally:
        db.close()
