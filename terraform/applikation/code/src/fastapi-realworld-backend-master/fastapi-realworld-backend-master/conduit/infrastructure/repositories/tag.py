from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.dtos.records.tag import TagRecordDTO
from conduit.infrastructure.models import Tag
from conduit.interfaces.repositories.tag import ITagRepository


class TagRepository(ITagRepository):
    """Repository for Tag model."""

    async def list(self, session: AsyncSession) -> list[TagRecordDTO]:
        query = select(Tag)
        tags = await session.scalars(query)
        return [self._to_tag_record_dto(tag) for tag in tags]

    @staticmethod
    def _to_tag_record_dto(model: Tag) -> TagRecordDTO:
        return TagRecordDTO(id=model.id, tag=model.tag, created_at=model.created_at)
