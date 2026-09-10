# Project: P04_fastapi_login
# Layer: Database/Repository - MUTATED
# Antipattern: Excessive Data / In-Memory Scan (Chen et al., 2014)

from app.db.models import User
from app.security import hash_password
from sqlalchemy.orm import Session


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