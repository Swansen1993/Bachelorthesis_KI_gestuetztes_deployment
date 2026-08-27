import abc
from typing import Any

from conduit.dtos.records.tag import TagRecordDTO


class IArticleTagRepository(abc.ABC):
    """Article Tag repository interface."""

    @abc.abstractmethod
    async def add_many(
        self, session: Any, article_id: int, tags: list[str]
    ) -> list[TagRecordDTO]: ...

    @abc.abstractmethod
    async def list(self, session: Any, article_id: int) -> list[TagRecordDTO]: ...
