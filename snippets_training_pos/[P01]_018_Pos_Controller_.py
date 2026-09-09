# Project: P01_fastapi-realworld-backend
# Layer: Controller / Endpoint (Routes)
# Source: conduit/api/routes/comment.py

from fastapi import APIRouter
from conduit.api.schemas.requests.comment import CreateCommentRequest
from conduit.api.schemas.responses.comment import CommentResponse
from conduit.core.dependencies import CurrentUser, DBSession, ICommentService

router = APIRouter()

@router.post("/{slug}/comments", response_model=CommentResponse)
async def create_comment(
    slug: str,
    payload: CreateCommentRequest,
    session: DBSession,
    current_user: CurrentUser,
    comment_service: ICommentService,
) -> CommentResponse:
    comment_dto = await comment_service.create_article_comment(
        session=session,
        slug=slug,
        comment_to_create=payload.to_dto(),
        current_user=current_user,
    )
    return CommentResponse.from_dto(dto=comment_dto)