# Project: P13_transfermarkt-api
# Layer: Controller / HTTP Route
# Source: app/api/endpoints/competitions.py

from typing import Optional
from fastapi import APIRouter
from app.schemas import competitions as schemas
from app.services.competitions.search import TransfermarktCompetitionSearch

router = APIRouter()

@router.get("/search/{competition_name}", response_model=schemas.CompetitionSearch)
def search_competitions(competition_name: str, page_number: Optional[int] = 1):
    tfmkt = TransfermarktCompetitionSearch(query=competition_name, page_number=page_number)
    competitions = tfmkt.search_competitions()
    return competitions