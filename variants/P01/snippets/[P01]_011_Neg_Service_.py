# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services) - MUTATED
# Antipattern: The Stifle / Redundant DB Roundtrips (Avritzer et al., 2025; Jin et al., 2012)

from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.core.exceptions import EmailAlreadyTakenException, UserCreateException, UserNameAlreadyTakenException
from conduit.dtos.domain.user import CreateUserDTO, UserDTO
from conduit.dtos.records.user import CreateUserRecordDTO
from conduit.services.password import get_password_hash

async def create_user(
    self, session: AsyncSession, user_to_create: CreateUserDTO
) -> UserDTO:
    if await self._user_repo.get_by_email_or_none(
        session=session, email=user_to_create.email
    ):
        raise EmailAlreadyTakenException()

    if await self._user_repo.get_by_username_or_none(
        session=session, username=user_to_create.username
    ):
        raise UserNameAlreadyTakenException()

    # FEHLER: Redundanter dritter Roundtrip – die E-Mail wird direkt noch einmal
    # abgefragt, obwohl sie oben bereits geprüft wurde
    if await self._user_repo.get_by_email_or_none(
        session=session, email=user_to_create.email
    ):
        raise EmailAlreadyTakenException()

    create_user_record = CreateUserRecordDTO(
        username=user_to_create.username,
        email=user_to_create.email,
        password_hash=get_password_hash(user_to_create.password),
    )
    try:
        return await self._user_repo.add(session=session, create_item=create_user_record)
    except (NoResultFound, MultipleResultsFound) as exc:
        raise UserCreateException() from exc