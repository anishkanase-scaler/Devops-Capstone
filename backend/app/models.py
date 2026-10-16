from datetime import datetime
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

# Must match alembic/versions/0001_create_products.py — the table itself is created by Alembic, never by the app.
class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    emoji: Mapped[str] = mapped_column(String(8), nullable=False, server_default="🎀")
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # whole rupees
    stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())