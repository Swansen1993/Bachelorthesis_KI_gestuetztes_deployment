# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services)
# Source: conduit/services/article.py

from sqlalchemy.ext.asyncio import AsyncSession
from conduit.core.exceptions import ArticlePermissionException
from conduit.dtos.domain.user import UserDTO

async def delete_article_by_slug(
    self, session: AsyncSession, slug: str, current_user: UserDTO
) -> None:
    article = await self._article_repo.get_by_slug(session=session, slug=slug)

    if article.author_id != current_user.id:
        raise ArticlePermissionException()

    await self._article_repo.delete_by_slug(session=session, slug=slug)