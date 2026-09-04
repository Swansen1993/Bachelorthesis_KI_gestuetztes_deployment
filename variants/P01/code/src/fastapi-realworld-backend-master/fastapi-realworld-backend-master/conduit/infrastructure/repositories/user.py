from collections.abc import Collection
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import UserNotFoundException
from conduit.dtos.domain.user import UserDTO
from conduit.dtos.records.user import CreateUserRecordDTO, UpdateUserRecordDTO
from conduit.infrastructure.models import User
from conduit.interfaces.repositories.user import IUserRepository


class UserRepository(IUserRepository):
    """Repository for User model."""

    async def add(
        self, session: AsyncSession, create_item: CreateUserRecordDTO
    ) -> UserDTO:
        query = (
            insert(User)
            .values(
                username=create_item.username,
                email=create_item.email,
                password_hash=create_item.password_hash,
                image="https://api.realworld.io/images/smiley-cyrus.jpeg",
                bio="",
                created_at=datetime.now(),
            )
            .returning(User)
        )
        result = await session.execute(query)
        return self._to_user_dto(result.scalar_one())

    async def get_by_email_or_none(
        self, session: AsyncSession, email: str
    ) -> UserDTO | None:
        query = select(User).where(User.email == email)
        if user := await session.scalar(query):
            return self._to_user_dto(user)
        return None

    async def get_by_email(self, session: AsyncSession, email: str) -> UserDTO:
        query = select(User).where(User.email == email)
        if not (user := await session.scalar(query)):
            raise UserNotFoundException()
        return self._to_user_dto(user)

    async def get_or_none(self, session: AsyncSession, user_id: int) -> UserDTO | None:
        query = select(User).where(User.id == user_id)
        if user := await session.scalar(query):
            return self._to_user_dto(user)
        return None

    async def get(self, session: AsyncSession, user_id: int) -> UserDTO:
        query = select(User).where(User.id == user_id)
        if not (user := await session.scalar(query)):
            raise UserNotFoundException()
        return self._to_user_dto(user)

    async def list_by_users(
        self, session: AsyncSession, user_ids: Collection[int]
    ) -> list[UserDTO]:
        query = select(User).where(User.id.in_(user_ids))
        users = await session.scalars(query)
        return [self._to_user_dto(user) for user in users]

    async def get_by_username_or_none(
        self, session: AsyncSession, username: str
    ) -> UserDTO | None:
        query = select(User).where(User.username == username)
        if user := await session.scalar(query):
            return self._to_user_dto(user)
        return None

    async def get_by_username(self, session: AsyncSession, username: str) -> UserDTO:
        query = select(User).where(User.username == username)
        if not (user := await session.scalar(query)):
            raise UserNotFoundException()
        return self._to_user_dto(user)

    async def update(
        self, session: AsyncSession, user_id: int, update_item: UpdateUserRecordDTO
    ) -> UserDTO:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(updated_at=datetime.now())
            .returning(User)
        )
        if update_item.username is not None:
            query = query.values(username=update_item.username)
        if update_item.email is not None:
            query = query.values(email=update_item.email)
        if update_item.password_hash is not None:
            query = query.values(password_hash=update_item.password_hash)
        if update_item.bio is not None:
            query = query.values(bio=update_item.bio)
        if update_item.image is not None:
            query = query.values(image=update_item.image)

        result = await session.execute(query)
        return self._to_user_dto(result.scalar_one())

    @staticmethod
    def _to_user_dto(model: User) -> UserDTO:
        return UserDTO(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            bio=model.bio,
            image=model.image,
            created_at=model.created_at,
        )
