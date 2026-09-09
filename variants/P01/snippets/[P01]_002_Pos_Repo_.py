# Project: P01_fastapi-realworld-backend
# Layer: Repository (Database I/O)
# Source: conduit/infrastructure/repositories/article.py

from sqlalchemy import select, exists, func
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.dtos.records.article import ArticleFeedRecordDTO
from conduit.infrastructure.models import Article, ArticleTag, Favorite, Follower, Tag, User

async def list_by_filters(
    self,
    session: AsyncSession,
    user_id: int | None,
    limit: int,
    offset: int,
    tag: str | None = None,
    author: str | None = None,
    favorited: str | None = None,
) -> list[ArticleFeedRecordDTO]:
    query = (
        select(
            Article.id.label("id"),
            Article.author_id.label("author_id"),
            Article.slug.label("slug"),
            Article.title.label("title"),
            Article.description.label("description"),
            Article.body.label("body"),
            Article.created_at.label("created_at"),
            Article.updated_at.label("updated_at"),
            User.username.label("username"),
            User.bio.label("bio"),
            User.image.label("image"),
            exists()
            .where(
                (Follower.follower_id == user_id)
                & (Follower.following_id == Article.author_id)
            )
            .label("following"),
            select(func.count(Favorite.article_id))
            .where(Favorite.article_id == Article.id)
            .scalar_subquery()
            .label("favorites_count"),
            exists()
            .where(
                (Favorite.user_id == user_id) & (Favorite.article_id == Article.id)
            )
            .label("favorited"),
            func.string_agg(Tag.tag, ", ").label("tags"),
        )
        .outerjoin(User, Article.author_id == User.id)
        .outerjoin(ArticleTag, Article.id == ArticleTag.article_id)
        .outerjoin(FavoriteAlias, FavoriteAlias.article_id == Article.id)
        .outerjoin(Tag, Tag.id == ArticleTag.tag_id)
        .group_by(
            Article.id, Article.author_id, Article.slug, Article.title,
            Article.description, Article.body, Article.created_at, Article.updated_at,
            User.id, User.username, User.bio, User.email, User.image,
        )
    )

    if author is not None:
        query = query.where(User.username == author)
    if tag is not None:
        query = query.where(Tag.tag == tag)

    query = query.limit(limit).offset(offset)
    articles = await session.execute(query)
    return [self._to_article_feed_record_dto(article) for article in articles]