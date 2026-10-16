from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Category = Literal["Beauty", "Accessories", "Home", "Stationery"]

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    emoji: str = Field(default="🎀", max_length=8)
    category: Category
    price: int = Field(ge=0)
    stock: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    # Every field is optional: PUT only changes what you send.
    name: str | None = Field(default=None, min_length=1, max_length=100)
    emoji: str | None = Field(default=None, max_length=8)
    category: Category | None = None
    price: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)

class ProductOut(ProductCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)