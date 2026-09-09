# Project: P01_fastapi-realworld-backend
# Layer: Repository (Database I/O)
# Source: conduit/infrastructure/repositories/follower.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.infrastructure.models import Follower

async def list(
    self, session: AsyncSession, follower_id: int, following_ids: list[int]
) -> list[int]:
    query = select(Follower.following_id).where(
        Follower.following_id.in_(following_ids),
        Follower.follower_id == follower_id,
    )
    result = await session.execute(query)
    return list(result.scalars())