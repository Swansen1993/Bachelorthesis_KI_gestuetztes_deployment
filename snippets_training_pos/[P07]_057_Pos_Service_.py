# Project: P07_ecommerce-backend
# Layer: Business Logic
# Source: Services/ProductServices/controller.py

from api.schemas import ProductCreate, InventoryCreate
from common.db.models.products import Product
from sqlalchemy.orm import Session

def create_product(product: ProductCreate, db: Session):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    inventory_data = InventoryCreate(
        category_name=db_product.category_name,
        product_id=db_product.id,
        inventory_quantity=db_product.current_inventory,
    )

    try:
        create_inventory(inventory_data, db)
    except Exception as error:
        print("Error creating inventory: ", error)

    return db_product