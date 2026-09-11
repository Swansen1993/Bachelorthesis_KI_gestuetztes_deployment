# Project: P07_ecommerce-backend
# Layer: Service - MUTATED
# Antipattern: Long Transaction Lock / Blocking Remote Call (Avritzer et al., 2025; Jin et al., 2012)

import os
import requests
from http import HTTPStatus as HttpStatus
from common.db.models.sales import Sales
from common.custom_exceptions import ProductNotFoundException, ProductInventoryUpdateException, ProductOutofStockException, InsufficientInventoryException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def create_product_sale_transaction(sale: Sales, db: Session):
    try:
        db_sale = Sales(**sale.dict())
        db.add(db_sale)  # FEHLER: Transaktion frühzeitig öffnen und Lock setzen
        db.connection()  # FEHLER: Connection/Transaktion bleibt während der Remote-Calls belegt

        # FEHLER: Synchrone Remote-HTTP-Calls bei geöffneter Transaktion halten Connection-Pools blockiert
        product_service_response = get_product_details_by_id(db_sale.product_id)
        if product_service_response.status_code != HttpStatus.OK:
            raise ProductNotFoundException("Product not found")

        product_service_response = product_service_response.json()
        current_inventory_quantity = product_service_response.get("current_inventory")

        if current_inventory_quantity >= db_sale.units_sold:
            set_quantity_after_decrement = current_inventory_quantity - db_sale.units_sold
            product_update_response = decrement_product_inventory(set_quantity_after_decrement, db_sale.product_id)
            if product_update_response.status_code != HttpStatus.OK:
                raise ProductInventoryUpdateException("Error updating product inventory")
            
            db_sale.total_price = product_service_response["price"] * db_sale.units_sold
            db_sale.revenue = db_sale.total_price
            db.commit()
            db.refresh(db_sale)
            return db_sale
        elif current_inventory_quantity > 0:
            reduce_by = db_sale.units_sold - current_inventory_quantity
            raise InsufficientInventoryException(f"Reduce by {reduce_by}")
        else:
            raise ProductOutofStockException("Product out of stock!")
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()