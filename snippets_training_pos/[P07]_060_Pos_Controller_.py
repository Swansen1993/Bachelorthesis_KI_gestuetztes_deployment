# Project: P07_ecommerce-backend
# Layer: Controller / HTTP API
# Source: Services/ProductServices/routes.py

from fastapi import APIRouter, Depends, HTTPException
from api.schemas import ProductUpdate
from api.controller import update_product_attribute
from common.db.session import get_db
from sqlalchemy.orm Session

router = APIRouter()

@router.put("/update", status_code=200)
def update_product(
    updated_attributes: ProductUpdate, product_id, db: Session = Depends(get_db)
):
    try:
        props_to_update = {
            key: value
            for key, value in updated_attributes.dict().items()
            if value is not None or key == "current_inventory"
        }

        db_product = update_product_attribute(product_id, props_to_update, db)
        return db_product

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")