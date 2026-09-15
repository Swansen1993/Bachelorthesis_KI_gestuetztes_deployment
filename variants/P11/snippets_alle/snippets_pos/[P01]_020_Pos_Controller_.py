# Project: P01_fastapi-realworld-backend
# Layer: Controller / Endpoint (Routes)
# Source: conduit/api/routes/users.py

from fastapi import APIRouter
from conduit.api.schemas.requests.user import UserUpdateRequest
from conduit.api.schemas.responses.user import UpdatedUserResponse
from conduit.core.dependencies import CurrentUser, DBSession, IUserService, JWTToken

router = APIRouter()

@router.put("", response_model=UpdatedUserResponse)
async def update_current_user(
    payload: UserUpdateRequest,
    token: JWTToken,
    session: DBSession,
    current_user: CurrentUser,
    user_service: IUserService,
) -> UpdatedUserResponse:
    updated_user_dto = await user_service.update_user(
        session=session, current_user=current_user, user_to_update=payload.to_dto()
    )
    return UpdatedUserResponse.from_dto(dto=updated_user_dto, token=token)