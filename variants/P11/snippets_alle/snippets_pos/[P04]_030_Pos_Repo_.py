# Project: P04_fastapi_login
# Layer: Database
# Source: examples/full-example/app/db/actions.py

from typing import Optional

from app.db import SessionLocal
from app.db.models import Post, User
from app.security import hash_password, manager
from sqlalchemy.orm import Session


def create_user(name: str, password: str, db: Session, is_admin: bool = False) -> User:
   
    hashed_pw = hash_password(password)
    user = User(username=name, password=hashed_pw, is_admin=is_admin)
    db.add(user)
    db.commit()
    return user