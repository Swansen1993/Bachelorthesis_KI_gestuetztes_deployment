# Project: P01_fastapi-realworld-backend
# Layer: Controller / Endpoint (Routes)
# Source: conduit/api/routes/article.py

from fastapi import APIRouter
from conduit.api.schemas.requests.article import CreateArticleRequest
from conduit.api.schemas.responses.article import ArticleResponse
from conduit.core.dependencies import CurrentUser, DBSession, IArticleService

router = APIRouter()

@router.post("", response_model=ArticleResponse)
async def create_article(
    payload: CreateArticleRequest,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    article_dto = await article_service.create_new_article(
        session=session, author_id=current_user.id, article_to_create=payload.to_dto()
    )
    return ArticleResponse.from_dto(dto=article_dto)