# Project: P08_FastAPI-RBAC-Microservice
# Layer: Database Query
# Source: app/crud.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List, Optional

from . import models, schemas
from datetime import datetime

def create_product(db: Session, product: schemas.ProductBase, seller_id: int = None) -> models.Product:
    product_data = product.dict()
    product_data.pop("seller_id", None)
    if seller_id is not None:
        product_data["seller_id"] = seller_id
    
    category = db.query(models.Category).filter(models.Category.id == product.category_id).first()
    if not category:
        raise ValueError(f"Category with id {product.category_id} not found")
        
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product