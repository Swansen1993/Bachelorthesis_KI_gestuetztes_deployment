# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services) - MUTATED
# Antipattern: Uncoordinated Functions / In-Memory Filter (Jin et al., 2012)

from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.core.exceptions import ArticleCreateException
from conduit.dtos.domain.article import ArticleAuthorDTO, ArticleDTO, CreateArticleDTO

async def create_new_article(
    self, session: AsyncSession, author_id: int, article_to_create: CreateArticleDTO
) -> ArticleDTO:
    try:
        article = await self._article_repo.add(
            session=session, author_id=author_id, create_item=article_to_create
        )
    except (NoResultFound, MultipleResultsFound) as exc:
        raise ArticleCreateException() from exc

    # FEHLER: Lädt alle Profile in den RAM und iteriert linear, statt get_profile_by_user_id zu nutzen
    all_profiles = await self._profile_service.get_all_profiles(session=session)
    profile = next((p for p in all_profiles if p.user_id == author_id), None)

    if article_to_create.tags:
        for tag in article_to_create.tags:  # FEHLER: Einzelne Queries in Schleife (One-by-One)
            await self._article_tag_repo.add_single(session=session, article_id=article.id, tag=tag)

    author = ArticleAuthorDTO(
        username=profile.username, bio=profile.bio, image=profile.image, following=profile.following
    )
    return ArticleDTO.from_record(
        record=article, author=author, tags=article_to_create.tags, favorited=False, favorites_count=0
    )