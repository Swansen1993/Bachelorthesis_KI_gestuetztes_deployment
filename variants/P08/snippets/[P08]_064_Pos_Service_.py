# Project: P08_FastAPI-RBAC-Microservice
# Layer: Business Logic
# Source: app/auth.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import Local_Session

def get_current_admin_or_seller(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role not in ["admin", "seller"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions - Admin or Seller access required"
        )
    return current_user