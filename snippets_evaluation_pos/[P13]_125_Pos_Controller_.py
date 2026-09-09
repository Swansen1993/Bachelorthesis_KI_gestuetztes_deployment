# Project: P13_transfermarkt-api
# Layer: Controller / HTTP Route
# Source: app/api/endpoints/players.py

from fastapi import APIRouter
from app.schemas import players as schemas
from app.services.players.stats import TransfermarktPlayerStats

router = APIRouter()

@router.get("/{player_id}/stats", response_model=schemas.PlayerStats, response_model_exclude_none=True)
def get_player_stats(player_id: str):
    tfmkt = TransfermarktPlayerStats(player_id=player_id)
    player_stats = tfmkt.get_player_stats()
    return player_stats