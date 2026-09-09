# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services)
# Source: conduit/services/comment.py

from sqlalchemy.ext.asyncio import AsyncSession
from conduit.dtos.domain.comment import CommentDTO, CommentsListDTO
from conduit.dtos.domain.user import UserDTO

async def get_article_comments(
    self, session: AsyncSession, slug: str, current_user: UserDTO | None = None
) -> CommentsListDTO:
    article = await self._article_repo.get_by_slug(session=session, slug=slug)
    comment_records = await self._comment_repo.list(
        session=session, article_id=article.id
    )
    profiles_map = await self._get_profiles_mapping(
        session=session, comments=comment_records, current_user=current_user
    )
    comments = [
        CommentDTO.from_record(
            comment_record_dto, profiles_map[comment_record_dto.author_id]
        )
        for comment_record_dto in comment_records
    ]
    comments_count = await self._comment_repo.count(
        session=session, article_id=article.id
    )
    return CommentsListDTO(comments=comments, comments_count=comments_count)