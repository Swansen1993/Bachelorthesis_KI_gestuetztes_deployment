# Project: P08_FastAPI-RBAC-Microservice
# Layer: Database Query
# Source: app/crud.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List, Optional

from . import models, schemas
from datetime import datetime

def create_order_from_cart_for_user(db: Session, user_id: int) -> models.Order:
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        raise ValueError("Cart not found for this user")

    address = db.query(models.Address).filter(models.Address.user_id == user_id).first()
    if not address:
        raise ValueError("Address not found for this user")

    cart_items = db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).all()
    if not cart_items:
        raise ValueError("Cart is empty")

    order = models.Order(user_id=user_id, address_id=address.id, total_amount=0)
    db.add(order)
    db.commit()
    db.refresh(order)

    total = 0
    for item in cart_items:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.add(order_item)
        total += item.quantity * item.product.price

    order.total_amount = total
    db.commit()
    db.refresh(order)

    for item in cart_items:
        try:
            db.delete(item)
        except Exception:
            pass
    db.commit()

    return order