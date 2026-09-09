# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services)
# Source: conduit/services/profile.py

from sqlalchemy.ext.asyncio import AsyncSession
from conduit.core.exceptions import OwnProfileFollowingException, ProfileAlreadyFollowedException
from conduit.dtos.domain.user import UserDTO

async def follow_user(
    self, session: AsyncSession, username: str, current_user: UserDTO
) -> None:
    if username == current_user.username:
        raise OwnProfileFollowingException()

    target_user = await self._user_service.get_user_by_username(
        session=session, username=username
    )
    if await self._follower_repo.exists(
        session, follower_id=current_user.id, following_id=target_user.id
    ):
        raise ProfileAlreadyFollowedException()

    await self._follower_repo.create(
        session=session, follower_id=current_user.id, following_id=target_user.id
    )