# Project: P13_transfermarkt-api
# Layer: Controller / HTTP Route
# Source: app/api/endpoints/players.py

from fastapi import APIRouter
from app.schemas import players as schemas
from app.services.players.transfers import TransfermarktPlayerTransfers

router = APIRouter()

@router.get("/{player_id}/transfers", response_model=schemas.PlayerTransfers, response_model_exclude_none=True)
def get_player_transfers(player_id: str):
    tfmkt = TransfermarktPlayerTransfers(player_id=player_id)
    player_market_value = tfmkt.get_player_transfers()
    return player_market_value