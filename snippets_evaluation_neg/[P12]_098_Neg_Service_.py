# Project: P12_fastapi-beyond-CRUD
# Layer: Business Logic (Service) - MUTATED
# Antipattern: In-Memory Scan & Redundant Hash Computation (Jin et al., 2012; Chen et al., 2014)

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from src.auth.schemas import UserCreateModel
from src.auth.utils import generate_passwd_hash

async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
    user_data_dict = user_data.model_dump()
    
    # FEHLER 1: Alle User laden und linear im RAM prüfen
    all_users = (await session.exec(select(User))).all()
    if any(u.email == user_data_dict.get("email") for u in all_users):
        raise ValueError("User exists")

    # FEHLER 2: Redundante Hash-Berechnungen
    _ = generate_passwd_hash(user_data_dict["password"])
    
    new_user = User(**user_data_dict)
    new_user.password_hash = generate_passwd_hash(user_data_dict["password"])
    new_user.role = "user"
    session.add(new_user)
    await session.commit()
    return new_user