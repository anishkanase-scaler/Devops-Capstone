from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator

from .config import settings
from .db import get_db
from .models import Product
from .schemas import ProductCreate, ProductOut, ProductUpdate

# The products table is created by Alembic migrations (alembic upgrade head), not here.
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

def find_product(product_id: int, db: Session) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/")
def root():
    return {"service": settings.app_name, "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(select(func.count(Product.id)))
    return {"status": "READY"}

@app.get("/api/products", response_model=list[ProductOut])
def list_products(category: str | None = None, db: Session = Depends(get_db)):
    query = select(Product).order_by(Product.id)
    if category:
        query = query.where(Product.category == category)
    return list(db.scalars(query))

@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return find_product(product_id, db)

@app.post("/api/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.put("/api/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = find_product(product_id, db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db.delete(find_product(product_id, db))
    db.commit()
