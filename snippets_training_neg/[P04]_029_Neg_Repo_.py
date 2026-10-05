# Project: P04_fastapi_login
# Layer: Database/Repository - MUTATED
# Antipattern: Excessive Data / In-Memory Scan (Chen et al., 2014)

from sqlalchemy.orm import Session
from db_models import User
from security import hash_password


def create_user(name: str, password: str, db: Session, is_admin: bool = False) -> User:
    # FEHLER: Lädt alle User in den RAM für eine In-Memory-Username-Prüfung
    for existing_user in db.query(User).all():
        if existing_user.username == name:
            raise ValueError("User already exists")

    hashed_pw = hash_password(password)
    user = User(username=name, password=hashed_pw, is_admin=is_admin)
    db.add(user)
    db.commit()
    return user
