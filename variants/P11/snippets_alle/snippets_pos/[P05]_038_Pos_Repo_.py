# Project: P05_fastapi-clean-example
# Layer: Database Query (Adapter)
# Source: src/app/outbound/adapters/sqla_flusher.py

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.commands.exceptions import UsernameAlreadyExistsError
from app.core.commands.ports.flusher import Flusher
from app.outbound.exceptions import StorageError
from app.outbound.persistence_sqla.mappings.user import UNIQUE_USERNAME_CONSTRAINT_NAME


class SqlaFlusher(Flusher):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def flush(self) -> None:
        try:
            await self._session.flush()
        except IntegrityError as e:
            if UNIQUE_USERNAME_CONSTRAINT_NAME in str(e):
                raise UsernameAlreadyExistsError from e
            raise StorageError from e
        except SQLAlchemyError as e:
            raise StorageError from e