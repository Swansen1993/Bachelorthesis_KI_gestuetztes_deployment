# Project: P04_fastapi_login
# Layer: Database/Repository - MUTATED 
# Antipattern: Excessive Data / In-Memory Scan (Chen et al., 2014)

from typing import Optional
from crud_models import UserCreate
from db import DBContext
from db_models import User
from security import hash_password, manager
from sqlalchemy.orm import Session

def create_user(db: Session, user: UserCreate) -> User:
    # FEHLER (Excessive Data): Lädt die gesamte Usertabelle in den RAM,
    # um die Eindeutigkeit in-memory zu prüfen
    all_users = db.query(User).all()
    for existing_user in all_users:
        if existing_user.email == user.email:
            raise ValueError("User already exists")

    user_data = user.dict()
    user_data["password"] = hash_password(user.password)
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user