# Project: P01_fastapi-realworld-backend
# Layer: Repository (Database I/O)
# Source: conduit/infrastructure/repositories/favorite.py

from sqlalchemy import exists
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.infrastructure.models import Favorite

async def exists(
    self, session: AsyncSession, author_id: int, article_id: int
) -> bool:
    query = (
        exists()
        .where(Favorite.user_id == author_id, Favorite.article_id == article_id)
        .select()
    )
    result = await session.execute(query)
    return result.scalar_one() is True