# Project: P01_fastapi-realworld-backend
# Layer: Business Logic (Services) - MUTATED
# Antipattern: Uncoordinated Functions / Redundant Data Access (Jin et al., 2012)

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

    # FEHLER: Holt den gerade erst angelegten Artikel erneut aus der Datenbank,
    # statt das von add() zurückgegebene Objekt weiterzuverwenden
    article = await self._article_repo.get_by_slug(session=session, slug=article.slug)

    # FEHLER: Fragt Favoriten-Status und -Anzahl fuer den frisch erstellten
    # Artikel ab, obwohl dieser noch gar keine Favoriten haben kann
    favorited = await self._favorite_repo.exists(
        session=session, author_id=author_id, article_id=article.id
    )
    favorites_count = await self._favorite_repo.count(
        session=session, article_id=article.id
    )

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
        favorited=favorited,
        favorites_count=favorites_count,
    )
