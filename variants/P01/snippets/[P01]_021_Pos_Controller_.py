# Project: P01_fastapi-realworld-backend
# Layer: Controller / Endpoint (Routes)
# Source: conduit/api/routes/users.py

from fastapi import APIRouter
from conduit.api.schemas.responses.user import CurrentUserResponse
from conduit.core.dependencies import CurrentUser, JWTToken

router = APIRouter()

@router.get("", response_model=CurrentUserResponse)
async def get_current_user(
    token: JWTToken, current_user: CurrentUser
) -> CurrentUserResponse:
    return CurrentUserResponse.from_dto(dto=current_user, token=token)