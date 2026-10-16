"""seed starter products

Revision ID: 0002_seed_products
Revises: 0001_create_products
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_seed_products"
down_revision = "0001_create_products"
branch_labels = None
depends_on = None

# A lightweight copy of the table for this migration only, so it doesn't depend on app/models.py.
products = sa.table(
    "products",
    sa.column("name", sa.String),
    sa.column("emoji", sa.String),
    sa.column("category", sa.String),
    sa.column("price", sa.Integer),
    sa.column("stock", sa.Integer),
)

SEED = [
    {"name": "Rose Quartz Roller", "emoji": "💎", "category": "Beauty", "price": 799, "stock": 42},
    {"name": "Strawberry Lip Balm", "emoji": "🍓", "category": "Beauty", "price": 199, "stock": 200},
    {"name": "Blush Silk Scrunchie", "emoji": "🎀", "category": "Accessories", "price": 149, "stock": 120},
    {"name": "Heart Sunglasses", "emoji": "🕶️", "category": "Accessories", "price": 599, "stock": 0},
    {"name": "Peony Scented Candle", "emoji": "🕯️", "category": "Home", "price": 499, "stock": 3},
    {"name": "Pastel Notebook", "emoji": "📓", "category": "Stationery", "price": 199, "stock": 90},
]


def upgrade():
    op.bulk_insert(products, SEED)


def downgrade():
    # Remove only the seeded rows; products added through the app stay.
    op.execute(products.delete().where(products.c.name.in_([p["name"] for p in SEED])))
