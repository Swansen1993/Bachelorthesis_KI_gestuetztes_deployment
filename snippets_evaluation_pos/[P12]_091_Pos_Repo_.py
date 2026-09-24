# Project: P12_fastapi-beyond-CRUD
# Layer: Database / IO (Query)
# Source: src/books/service.py

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Book

async def get_user_books(self, user_uid: str, session: AsyncSession):
    statement = (
        select(Book)
        .where(Book.user_uid == user_uid)
        .order_by(desc(Book.created_at))
    )
    result = await session.exec(statement)
    return result.all()