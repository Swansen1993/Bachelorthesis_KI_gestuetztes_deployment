# Project: P01_fastapi-realworld-backend
# Layer: Controller / Endpoint (Routes)
# Source: conduit/api/routes/article.py

from fastapi import APIRouter
from conduit.api.schemas.responses.article import ArticlesFeedResponse
from conduit.core.dependencies import CurrentOptionalUser, DBSession, IArticleService, Pagination, QueryFilters

router = APIRouter()

@router.get("", response_model=ArticlesFeedResponse)
async def get_global_article_feed(
    pagination: Pagination,
    articles_filters: QueryFilters,
    session: DBSession,
    current_user: CurrentOptionalUser,
    article_service: IArticleService,
) -> ArticlesFeedResponse:
    articles_feed_dto = await article_service.get_articles_by_filters(
        session=session,
        current_user=current_user,
        tag=articles_filters.tag,
        author=articles_filters.author,
        favorited=articles_filters.favorited,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return ArticlesFeedResponse.from_dto(dto=articles_feed_dto)