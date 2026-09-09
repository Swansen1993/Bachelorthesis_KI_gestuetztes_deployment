# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services)
# Source: conduit/services/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from conduit.core.exceptions import IncorrectLoginInputException, UserNotFoundException
from conduit.dtos.domain.auth import AuthResult
from conduit.dtos.domain.user import LoginUserDTO
from conduit.services.password import verify_password

async def sign_in_user(
    self, session: AsyncSession, user_to_login: LoginUserDTO
) -> AuthResult:
    try:
        user = await self._user_service.get_user_by_email(
            session=session, email=user_to_login.email
        )
    except UserNotFoundException:
        raise IncorrectLoginInputException()

    if not verify_password(
        plain_password=user_to_login.password, hashed_password=user.password_hash
    ):
        raise IncorrectLoginInputException()

    jwt_token = self._auth_token_service.generate_jwt_token(user=user)
    return user, jwt_token