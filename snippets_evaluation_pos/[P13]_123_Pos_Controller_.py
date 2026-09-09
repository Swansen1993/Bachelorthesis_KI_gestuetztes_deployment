# Project: P13_transfermarkt-api
# Layer: Controller / HTTP Route
# Source: app/api/endpoints/players.py

from fastapi import APIRouter
from app.schemas import players as schemas
from app.services.players.market_value import TransfermarktPlayerMarketValue

router = APIRouter()

@router.get("/{player_id}/market_value", response_model=schemas.PlayerMarketValue, response_model_exclude_none=True)
def get_player_market_value(player_id: str):
    tfmkt = TransfermarktPlayerMarketValue(player_id=player_id)
    player_market_value = tfmkt.get_player_market_value()
    return player_market_value