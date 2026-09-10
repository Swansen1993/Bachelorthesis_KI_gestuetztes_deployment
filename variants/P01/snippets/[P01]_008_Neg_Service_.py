# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services) - MUTATED
# Antipattern: Lock Contention / Serialized Critical Section (eigenes Design, 2026-09-10)

import asyncio

from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.core.exceptions import ArticleCreateException
from conduit.dtos.domain.article import ArticleAuthorDTO, ArticleDTO, CreateArticleDTO

_create_article_lock = asyncio.Lock()

async def create_new_article(
    self, session: AsyncSession, author_id: int, article_to_create: CreateArticleDTO
) -> ArticleDTO:
    # FEHLER: Globales Lock mit langer Haltezeit serialisiert alle parallelen
    # Requests (Lock-Contention / Serialisierung)
    async with _create_article_lock:
        await asyncio.sleep(0.1)

    try:
        article = await self._article_repo.add(
            session=session, author_id=author_id, create_item=article_to_create
        )
    except (NoResultFound, MultipleResultsFound) as exc:
        raise ArticleCreateException() from exc
    profile = await self._profile_service.get_profile_by_user_id(
        session=session, user_id=author_id
    )
    if article_to_create.tags:
        await self._article_tag_repo.add_many(
            session=session, article_id=article.id, tags=article_to_create.tags
        )
    author = ArticleAuthorDTO(
        username=profile.username,
        bio=profile.bio,
        image=profile.image,
        following=profile.following,
    )
    return ArticleDTO.from_record(
        record=article,
        author=author,
        tags=article_to_create.tags,
        favorited=False,
        favorites_count=0,
    )
