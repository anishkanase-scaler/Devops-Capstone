"""create products table

Revision ID: 0001_create_products
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_products"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("emoji", sa.String(length=8), nullable=False, server_default="🎀"),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("products")
