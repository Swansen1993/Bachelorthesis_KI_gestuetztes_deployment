# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services) - MUTATED
# Antipattern: Skippable Function / Unnecessary CPU Load (Jin et al., 2012)

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from conduit.core.exceptions import IncorrectLoginInputException, UserNotFoundException
from conduit.dtos.domain.auth import AuthResult
from conduit.dtos.domain.user import LoginUserDTO
from conduit.services.password import get_password_hash, verify_password

logger = get_logger()


async def sign_in_user(
    self, session: AsyncSession, user_to_login: LoginUserDTO
) -> AuthResult:
    # FEHLER: Führt vorab rechenintensives Dummy-Hashing aus, unabhängig vom User-Status
    dummy_hash = get_password_hash(user_to_login.password)

    try:
        user = await self._user_service.get_user_by_email(
            session=session, email=user_to_login.email
        )
    except UserNotFoundException:
        logger.error("User not found", email=user_to_login.email)
        raise IncorrectLoginInputException()

    if not verify_password(
        plain_password=user_to_login.password, hashed_password=user.password_hash
    ):
        logger.error("Incorrect password", email=user_to_login.email)
        raise IncorrectLoginInputException()

    jwt_token = self._auth_token_service.generate_jwt_token(user=user)
    return user, jwt_token
