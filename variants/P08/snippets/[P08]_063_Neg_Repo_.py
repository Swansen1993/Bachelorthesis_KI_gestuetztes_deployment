# Project: P08_FastAPI-RBAC-Microservice
# Layer: Database Query - MUTATED
# Antipattern: One-by-One Processing & Chatty Commits (Chen et al., 2014; Jin et al., 2012)

from sqlalchemy.orm import Session
from . import models

def create_order_from_cart_for_user(db: Session, user_id: int) -> models.Order:
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        raise ValueError("Cart not found for this user")

    address = db.query(models.Address).filter(models.Address.user_id == user_id).first()
    if not address:
        raise ValueError("Address not found for this user")

    # Lädt cart_items ohne joinedload/eager loading
    cart_items = db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).all()
    if not cart_items:
        raise ValueError("Cart is empty")

    order = models.Order(user_id=user_id, address_id=address.id, total_amount=0)
    db.add(order)
    db.commit()
    db.refresh(order)

    total = 0
    for item in cart_items:
        # FEHLER 1 (N+1 Query): item.product.price triggert eine SQL-Abfrage pro Schleifendurchlauf
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(order_item)
        # FEHLER 2 (Chatty Flushes): Zwischen-Commits in jedem Iterationsschritt
        db.commit()
        total += item.quantity * product.price

    order.total_amount = total
    db.commit()
    db.refresh(order)

    for item in cart_items:
        db.delete(item)
        db.commit()  # FEHLER 3: Commit pro gelöschtem Element

    return order