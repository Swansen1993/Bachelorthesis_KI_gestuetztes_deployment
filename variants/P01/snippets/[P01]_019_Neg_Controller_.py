# Project: P01_fastapi-realworld-backend
# Layer: Controller / Endpoint (Routes) - MUTATED
# Antipattern: Traffic Jam & Blocking Sync I/O (Avritzer et al., 2025; Jin et al., 2012)

import time
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
    """
    Follow profile with specific username.
    """
    # FEHLER: Blockierender synchroner Call im Event-Loop
    time.sleep(0.3)

    await profile_service.follow_user(
        session=session, username=username, current_user=current_user
    )
    profile_dto = await profile_service.get_profile_by_username(
        session=session, username=username, current_user=current_user
    )
    return ProfileResponse.from_dto(dto=profile_dto)
