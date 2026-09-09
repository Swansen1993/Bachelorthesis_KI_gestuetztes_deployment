# Project: P01_fastapi-realworld-backend
# Layer: Repository (Database I/O) - MUTATED
# Antipattern: One-by-One Processing / The Stifle (Chen et al., 2014; Avritzer et al., 2025)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from conduit.dtos.records.article import ArticleFeedRecordDTO
from conduit.infrastructure.models import (
    Article,
    ArticleTag,
    Favorite,
    Follower,
    Tag,
    User,
)


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

    query = select(Article)
    res = await session.execute(query)
    all_articles = res.scalars().all()

    filtered = []
    for art in all_articles:

        user_res = await session.execute(select(User).where(User.id == art.author_id))
        user = user_res.scalar_one_or_none()
        if author and (not user or user.username != author):
            continue

        fav_count = await session.scalar(
            select(func.count(Favorite.article_id)).where(Favorite.article_id == art.id)
        )
        is_fav = bool(
            await session.scalar(
                select(Favorite).where(
                    Favorite.user_id == user_id, Favorite.article_id == art.id
                )
            )
        )
        is_following = bool(
            await session.scalar(
                select(Follower).where(
                    Follower.follower_id == user_id,
                    Follower.following_id == art.author_id,
                )
            )
        )

        filtered.append(
            self._to_feed_dto_manual(
                art,
                user,
                fav_count=fav_count or 0,
                favorited=is_fav,
                following=is_following,
            )
        )

    return filtered[offset : offset + limit]
