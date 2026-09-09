# Project: P01_fastapi-realworld-backend
# Layer: Repository (Database I/O)
# Source: conduit/infrastructure/repositories/comment.py

from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.dtos.domain.comment import CreateCommentDTO
from conduit.dtos.records.comment import CommentRecordDTO
from conduit.infrastructure.models import Comment

async def add(
    self,
    session: AsyncSession,
    author_id: int,
    article_id: int,
    create_item: CreateCommentDTO,
) -> CommentRecordDTO:
    query = (
        insert(Comment)
        .values(
            author_id=author_id,
            article_id=article_id,
            body=create_item.body,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        .returning(Comment)
    )
    result = await session.execute(query)
    return self._to_comment_record_dto(result.scalar_one())