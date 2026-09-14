# Project: P07_ecommerce-backend
# Layer: Service - MUTATED
# Antipattern: Over-Committing & Chatty Flushes (Jin et al., 2012; Avritzer et al., 2025)

from common.db.models.products import Product
from api.schemas import InventoryCreate
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def update_product_attribute(product_id: int, updated_attributes: dict, db: Session):
    try:
        db_product = db.query(Product).filter_by(id=product_id).first()
        if db_product:
            for key, value in updated_attributes.items():
                if hasattr(db_product, key):
                    setattr(db_product, key, value)
                    # FEHLER: Commit & Refresh nach jedem einzelnen Feld
                    db.commit()
                    db.refresh(db_product)

            if "current_inventory" in updated_attributes:
                inventory_data = InventoryCreate(
                    product_id=product_id,
                    category_name=db_product.category_name,
                    inventory_quantity=updated_attributes["current_inventory"],
                )
                create_inventory(inventory_data, db)
                db.commit()
                db.refresh(db_product)

            return {"success": True, "message": "Updated", "product": db_product}
        return {"success": False, "message": "Not found"}
    except SQLAlchemyError as e:
        db.rollback()
        return {"success": False, "message": str(e)}