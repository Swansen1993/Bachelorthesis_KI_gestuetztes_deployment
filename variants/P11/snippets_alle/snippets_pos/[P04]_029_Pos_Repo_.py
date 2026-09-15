# Project: P04_fastapi_login
# Layer: Database
# Source: db_actions.py

from typing import Optional

from crud_models import UserCreate
from db import DBContext
from db_models import User
from security import hash_password, manager
from sqlalchemy.orm import Session


def create_user(db: Session, user: UserCreate) -> User:
    user_data = user.dict()
    user_data["password"] = hash_password(user.password)
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user