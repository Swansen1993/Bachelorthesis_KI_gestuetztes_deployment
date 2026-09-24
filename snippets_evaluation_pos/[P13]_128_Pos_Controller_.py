# Project: P13_transfermarkt-api
# Layer: Controller / HTTP Route
# Source: app/api/endpoints/players.py

from typing import Optional
from fastapi import APIRouter
from app.schemas import players as schemas
from app.services.players.search import TransfermarktPlayerSearch

router = APIRouter()

@router.get("/search/{player_name}", response_model=schemas.PlayerSearch, response_model_exclude_none=True)
def search_players(player_name: str, page_number: Optional[int] = 1):
    tfmkt = TransfermarktPlayerSearch(query=player_name, page_number=page_number)
    found_players = tfmkt.search_players()
    return found_players