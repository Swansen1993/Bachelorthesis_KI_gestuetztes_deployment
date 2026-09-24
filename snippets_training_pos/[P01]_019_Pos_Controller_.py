# Project: P01_fastapi-realworld-backend
# Layer: Controller / Endpoint (Routes)
# Source: conduit/api/routes/profile.py

from fastapi import APIRouter
from conduit.api.schemas.responses.profile import ProfileResponse
from conduit.core.dependencies import CurrentUser, DBSession, IProfileService

router = APIRouter()

@router.post("/{username}/follow", response_model=ProfileResponse)
async def follow_username(
    username: str,
    session: DBSession,
    current_user: CurrentUser,
    profile_service: IProfileService,
) -> ProfileResponse:
    await profile_service.follow_user(
        session=session, username=username, current_user=current_user
    )
    profile_dto = await profile_service.get_profile_by_username(
        session=session, username=username, current_user=current_user
    )
    return ProfileResponse.from_dto(dto=profile_dto)