# Project: P13_transfermarkt-api
# Layer: Controller / HTTP Route
# Source: app/api/endpoints/players.py

from fastapi import APIRouter
from app.schemas import players as schemas
from app.services.players.profile import TransfermarktPlayerProfile

router = APIRouter()

@router.get("/{player_id}/profile", response_model=schemas.PlayerProfile, response_model_exclude_none=True)
def get_player_profile(player_id: str):
    tfmkt = TransfermarktPlayerProfile(player_id=player_id)
    player_info = tfmkt.get_player_profile()
    return player_info