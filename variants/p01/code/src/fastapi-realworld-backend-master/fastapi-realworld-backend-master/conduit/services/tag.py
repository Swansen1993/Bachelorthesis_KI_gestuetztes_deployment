from sqlalchemy.ext.asyncio import AsyncSession

from conduit.dtos.domain.tag import TagDTO
from conduit.interfaces.repositories.tag import ITagRepository
from conduit.interfaces.services.tag import ITagService


class TagService(ITagService):
    """Service to handle article tags logic."""

    def __init__(self, tag_repo: ITagRepository):
        self._tag_repo = tag_repo

    async def get_all_tags(self, session: AsyncSession) -> list[TagDTO]:
        tags = await self._tag_repo.list(session=session)
        return [TagDTO.from_record(record=tag) for tag in tags]
