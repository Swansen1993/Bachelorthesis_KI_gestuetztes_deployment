# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services) - MUTATED
# Antipattern: Lock Granularity / Coarse Critical Section (eigenes Design, 2026-09-10)

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.core.exceptions import (
    OwnProfileFollowingException,
    ProfileAlreadyFollowedException,
)
from conduit.dtos.domain.user import UserDTO

_follow_lock = asyncio.Lock()


async def follow_user(
    self, session: AsyncSession, username: str, current_user: UserDTO
) -> None:
    if username == current_user.username:
        raise OwnProfileFollowingException()

    # FEHLER:  Lock mit unnötiger Haltezeit serialisiert (Abfrage hintereinander) alle Follows
    async with _follow_lock:
        await asyncio.sleep(0.02)
        target_user = await self._user_service.get_user_by_username(
            session=session, username=username
        )
        if await self._follower_repo.exists(
            session, follower_id=current_user.id, following_id=target_user.id
        ):
            raise ProfileAlreadyFollowedException()

        await self._follower_repo.create(
            session=session,
            follower_id=current_user.id,
            following_id=target_user.id,
        )
