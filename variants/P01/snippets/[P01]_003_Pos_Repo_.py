# Project: P01_fastapi-realworld-backend
# Layer: Repository (Database I/O)
# Source: conduit/infrastructure/repositories/article_tag.py

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.dtos.records.tag import TagRecordDTO
from conduit.infrastructure.models import ArticleTag, Tag

async def add_many(
    self, session: AsyncSession, article_id: int, tags: list[str]
) -> list[TagRecordDTO]:
    insert_query = (
        insert(Tag)
        .on_conflict_do_nothing()
        .values([dict(tag=tag, created_at=datetime.now()) for tag in tags])
    )
    await session.execute(insert_query)

    select_query = select(Tag).where(Tag.tag.in_(tags))
    selected_tags = await session.scalars(select_query)
    tag_records = [self._to_tag_record_dto(tag) for tag in selected_tags]

    link_query = (
        insert(ArticleTag)
        .on_conflict_do_nothing()
        .values(
            [
                dict(
                    article_id=article_id,
                    tag_id=tag_record.id,
                    created_at=datetime.now(),
                )
                for tag_record in tag_records
            ]
        )
    )
    await session.execute(link_query)
    return tag_records