# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O Parser
# Source: app/services/competitions/search.py

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Competitions

def parse_search_results(self: TransfermarktBase) -> list:
    idx = [extract_from_url(url) for url in self.get_list_by_xpath(Competitions.Search.URLS)]
    name = self.get_list_by_xpath(Competitions.Search.NAMES)
    country = self.get_list_by_xpath(Competitions.Search.COUNTRIES)
    clubs = self.get_list_by_xpath(Competitions.Search.CLUBS)
    players = self.get_list_by_xpath(Competitions.Search.PLAYERS)
    total_market_value = self.get_list_by_xpath(Competitions.Search.TOTAL_MARKET_VALUES)
    mean_market_value = self.get_list_by_xpath(Competitions.Search.MEAN_MARKET_VALUES)
    continent = self.get_list_by_xpath(Competitions.Search.CONTINENTS)

    return [
        {
            "id": idx,
            "name": name,
            "country": country,
            "clubs": clubs,
            "players": players,
            "totalMarketValue": total_market_value,
            "meanMarketValue": mean_market_value,
            "continent": continent,
        }
        for idx, name, country, clubs, players, total_market_value, mean_market_value, continent in zip(
            idx, name, country, clubs, players, total_market_value, mean_market_value, continent
        )
    ]