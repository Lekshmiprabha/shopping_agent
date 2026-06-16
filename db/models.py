import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
ORM models that match the schema in store.db exactly.

Tables:
  products  — id, name, category, price, description, is_organic
  orders    — id, product_id, product_name, price, ordered_at
  reviews   — id, product_id, rating, reviewer_name, review_text
"""
from datetime import datetime
from sqlalchemy import Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base


class Product(Base):
    __tablename__ = "products"

    id:          Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:        Mapped[str]   = mapped_column(Text, nullable=False)
    category:    Mapped[str]   = mapped_column(Text, nullable=True)
    price:       Mapped[float] = mapped_column(Float, nullable=True)
    description: Mapped[str]   = mapped_column(Text, nullable=True)
    is_organic:  Mapped[int]   = mapped_column(Integer, default=0)   # 1 = organic

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "name":        self.name,
            "category":    self.category,
            "price":       self.price,
            "description": self.description,
            "is_organic":  bool(self.is_organic),
        }

    def __repr__(self):
        return f"<Product id={self.id} name={self.name!r}>"


class Order(Base):
    __tablename__ = "orders"

    id:           Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id:   Mapped[int]   = mapped_column(Integer, nullable=False)
    product_name: Mapped[str]   = mapped_column(Text, nullable=False)
    price:        Mapped[float] = mapped_column(Float, nullable=False)
    ordered_at:   Mapped[str]   = mapped_column(Text, nullable=False,
                                    default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "product_id":   self.product_id,
            "product_name": self.product_name,
            "price":        self.price,
            "ordered_at":   self.ordered_at,
        }

    def __repr__(self):
        return f"<Order id={self.id} product={self.product_name!r}>"


class Review(Base):
    __tablename__ = "reviews"

    id:            Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id:    Mapped[int]   = mapped_column(Integer, nullable=True)
    rating:        Mapped[float] = mapped_column(Float, nullable=True)
    reviewer_name: Mapped[str]   = mapped_column(Text, nullable=True)
    review_text:   Mapped[str]   = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "product_id":    self.product_id,
            "rating":        self.rating,
            "reviewer_name": self.reviewer_name,
            "review_text":   self.review_text,
        }
