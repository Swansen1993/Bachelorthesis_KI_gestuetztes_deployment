# Project: P12_fastapi-beyond-CRUD
# Layer: Database / IO (Query)
# Source: src/auth/service.py

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import User

async def get_user_by_email(self, email: str, session: AsyncSession):
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    user = result.first()
    return user