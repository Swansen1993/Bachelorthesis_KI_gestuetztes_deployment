# Project: P01_fastapi-realworld-backend
# Layer: Repository (Database I/O)
# Source: conduit/infrastructure/repositories/article.py

from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.core.utils.slug import make_slug_from_title
from conduit.dtos.domain.article import CreateArticleDTO
from conduit.dtos.records.article import ArticleRecordDTO
from conduit.infrastructure.models import Article

async def add(
    self, session: AsyncSession, author_id: int, create_item: CreateArticleDTO
) -> ArticleRecordDTO:
    query = (
        insert(Article)
        .values(
            author_id=author_id,
            slug=make_slug_from_title(title=create_item.title),
            title=create_item.title,
            description=create_item.description,
            body=create_item.body,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        .returning(Article)
    )
    result = await session.execute(query)
    return self._to_article_record_dto(result.scalar_one())