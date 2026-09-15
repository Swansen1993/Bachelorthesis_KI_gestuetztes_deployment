# Project: P08_FastAPI-RBAC-Microservice
# Layer: Controller
# Source: app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from typing import Optional

from . import crud, models, schemas
import os
from .database import Local_Session, engine
from .auth import create_access_token, get_current_user, get_current_admin, get_current_seller, get_current_admin_or_seller

@app.post("/orders/", response_model=schemas.Order, tags=["Orders"], summary="Create an order from the current user's cart")
def create_order_from_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        return crud.create_order_from_cart_for_user(db=db, user_id=current_user.id)
    except ValueError as e:
        msg = str(e).lower()
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=str(e))
        if "empty" in msg:
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))