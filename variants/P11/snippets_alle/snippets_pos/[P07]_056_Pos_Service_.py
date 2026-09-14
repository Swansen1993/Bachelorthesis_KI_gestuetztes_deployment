# Project: P07_ecommerce-backend
# Layer: Business Logic
# Source: Services/SalesServices/controller.py

import os
import requests
from http import HTTPStatus as HttpStatus
from common.db.models.sales import Sales
from common.custom_exceptions import (ProductNotFoundException,ProductInventoryUpdateException,ProductOutofStockException,InsufficientInventoryException,)
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def create_product_sale_transaction(sale: Sales, db: Session):
    try:
        db_sale = Sales(**sale.dict())
        product_service_response = get_product_details_by_id(db_sale.product_id)

        if product_service_response.status_code != HttpStatus.OK:
            raise ProductNotFoundException("Product not found")

        product_service_response = product_service_response.json()
        current_inventory_quantity = product_service_response.get("current_inventory")

        if current_inventory_quantity >= db_sale.units_sold:
            set_quantity_after_decrement = (
                current_inventory_quantity - db_sale.units_sold
            )
            product_update_response = decrement_product_inventory(
                set_quantity_after_decrement, db_sale.product_id
            )
            if product_update_response.status_code != HttpStatus.OK:
                raise ProductInventoryUpdateException(
                    "Error updating product inventory"
                )
            else:
                db_sale.total_price = (
                    product_service_response["price"] * db_sale.units_sold
                )
                db_sale.revenue = db_sale.total_price
                db.add(db_sale)
                db.commit()
                db.refresh(db_sale)
                return db_sale
        elif current_inventory_quantity > 0:
            reduce_by = db_sale.units_sold - current_inventory_quantity
            raise InsufficientInventoryException(
                f"Insufficient inventory for full order. You can order a reduced quantity, please reduce the quantity by {reduce_by}"
            )
        else:
            raise ProductOutofStockException("Product has gone out of stock!")

    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()