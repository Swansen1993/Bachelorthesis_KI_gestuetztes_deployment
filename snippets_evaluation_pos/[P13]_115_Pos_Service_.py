# Project: P13_transfermarkt-api
# Layer: Business Logic (Service)
# Source: app/services/clubs/search.py

from dataclasses import dataclass
from app.services.base import TransfermarktBase
from app.utils.xpath import Clubs

@dataclass
class TransfermarktClubSearch(TransfermarktBase):
    query: str = None
    page_number: int = 1

    def search_clubs(self) -> dict:
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_last_page_number(Clubs.Search.BASE)
        self.response["results"] = self._parse_search_results()
        return self.response