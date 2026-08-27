import abc

from sqlalchemy.ext.asyncio import AsyncSession

from conduit.dtos.records.tag import TagRecordDTO


class ITagRepository(abc.ABC):
    @abc.abstractmethod
    async def list(self, session: AsyncSession) -> list[TagRecordDTO]: ...
