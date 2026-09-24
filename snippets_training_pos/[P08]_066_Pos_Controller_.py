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

@app.post("/signup", response_model=schemas.User, status_code=201, tags=["Auth"], summary="Register a new user")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if getattr(user, "role", None) == "admin":
        raise HTTPException(status_code=403, detail="Cannot create admin via this endpoint")

    if getattr(user, "role", None) and user.role not in ("customer", "seller"):
        raise HTTPException(status_code=400, detail="Invalid role")

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)