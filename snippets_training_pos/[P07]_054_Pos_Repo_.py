# Project: P07_ecommerce-backend
# Layer: Database Access
# Source: Services/ProductServices/controller.py

from common.db.models.products import Product
from common.custom_exceptions import ProductNotFoundException
from sqlalchemy.orm import Session

def get_product_by_id(product_id: int, db: Session):
    result = db.query(Product).filter(Product.id == product_id).first()
    if result is None:
        raise ProductNotFoundException("Product not found")
    return result