# Project: P01_fastapi-realworld-backend
# Layer: Repository (Database I/O)
# Source: conduit/infrastructure/repositories/follower.py

from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.infrastructure.models import Follower

async def create(
    self, session: AsyncSession, follower_id: int, following_id: int
) -> None:
    query = insert(Follower).values(
        follower_id=follower_id,
        following_id=following_id,
        created_at=datetime.now(),
    )
    await session.execute(query)