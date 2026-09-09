# Project: P12_fastapi-beyond-CRUD
# Layer: Business Logic (Service)
# Source: src/auth/service.py

from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User
from src.auth.schemas import UserCreateModel
from src.auth.utils import generate_passwd_hash

async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
    user_data_dict = user_data.model_dump()
    new_user = User(**user_data_dict)
    new_user.password_hash = generate_passwd_hash(user_data_dict["password"])
    new_user.role = "user"
    session.add(new_user)
    await session.commit()
    return new_user