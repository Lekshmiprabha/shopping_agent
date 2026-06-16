"""
Checkout Agent
──────────────
Writes a confirmed order to the orders table in store.db.
Matches the existing schema: id, product_id, product_name, price, ordered_at
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger
from db.database import SessionLocal
from db.models import Order


def run(product_id: int, product_name: str, price: float) -> dict:
    """
    Insert one order row.

    Returns
    -------
    {
        "success":  bool,
        "order":    dict | None,
        "message":  str,
    }
    """
    logger.info(f"[CheckoutAgent] ordering product_id={product_id} name={product_name!r} price={price}")
    db = SessionLocal()
    try:
        order = Order(
            product_id   = product_id,
            product_name = product_name,
            price        = price,
            ordered_at   = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        logger.info(f"[CheckoutAgent] Order #{order.id} placed successfully.")
        return {
            "success": True,
            "order":   order.to_dict(),
            "message": (
                f"✅ Order placed successfully!\n\n"
                f"**Order #{order.id}**\n"
                f"- Product: {product_name}\n"
                f"- Price: ₹{price:.2f}\n"
                f"- Placed at: {order.ordered_at}"
            ),
        }
    except Exception as e:
        db.rollback()
        logger.error(f"[CheckoutAgent] Failed: {e}")
        return {"success": False, "order": None,
                "message": f"❌ Order failed: {str(e)}"}
    finally:
        db.close()


def get_all_orders() -> list[dict]:
    """Return all orders for the order history tab."""
    db = SessionLocal()
    try:
        return [
            o.to_dict()
            for o in db.query(Order).order_by(Order.id.desc()).all()
        ]
    finally:
        db.close()
