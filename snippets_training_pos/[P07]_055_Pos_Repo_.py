# Project: P07_ecommerce-backend
# Layer: Database Access
# Source: Services/ProductServices/controller.py

from common.db.models.inventory import Inventory
from common.custom_exceptions import ProductNotFoundException
from sqlalchemy.orm import Session

def get_product_inventory_history(product_id: int, db: Session):
    result = db.query(Inventory).filter(Inventory.product_id == product_id).all()

    if result is None:
        raise ProductNotFoundException("Product not found")
    return result