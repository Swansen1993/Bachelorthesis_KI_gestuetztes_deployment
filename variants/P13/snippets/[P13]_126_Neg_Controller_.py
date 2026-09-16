# Project: P13_transfermarkt-api
# Layer: Controller / HTTP Route - MUTATED
# Antipattern: Skippable Function / Redundant Re-Execution (Jin et al., 2012)

from typing import Optional
from fastapi import APIRouter
from app.schemas import competitions as schemas
from app.services.competitions.search import TransfermarktCompetitionSearch

router = APIRouter()

@router.get("/search/{competition_name}", response_model=schemas.CompetitionSearch)
def search_competitions(competition_name: str, page_number: Optional[int] = 1):
    tfmkt = TransfermarktCompetitionSearch(query=competition_name, page_number=page_number)
    
    # FEHLER: Führt den vollständigen Scraping- und Parsing-Vorgang redundant aus
    _ = tfmkt.search_competitions()
    
    competitions = tfmkt.search_competitions()
    return competitions