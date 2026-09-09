# Project: P01_fastapi-realworld-backend
# Layer: Controller / Endpoint (Routes)
# Source: conduit/api/routes/authentication.py

from fastapi import APIRouter
from conduit.api.schemas.requests.user import UserLoginRequest
from conduit.api.schemas.responses.user import UserLoginResponse
from conduit.core.dependencies import DBSession, IUserAuthService

router = APIRouter()

@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    payload: UserLoginRequest, session: DBSession, user_auth_service: IUserAuthService
) -> UserLoginResponse:
    user_dto, token = await user_auth_service.sign_in_user(
        session=session, user_to_login=payload.to_dto()
    )
    return UserLoginResponse.from_user(dto=user_dto, token=token)