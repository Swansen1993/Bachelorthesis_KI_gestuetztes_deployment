# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O Parser - MUTATED
# Antipattern: One-by-One Processing & Redundant DOM Scans (Chen et al., 2014; Jin et al., 2012)

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Competitions

def parse_search_results(self: TransfermarktBase) -> list:
    urls = self.get_list_by_xpath(Competitions.Search.URLS)
    results = []

    # FEHLER: Vollständige XPath-Auswertungen werden für jede URL in der Schleife wiederholt
    for url in urls:
        name = self.get_list_by_xpath(Competitions.Search.NAMES)
        country = self.get_list_by_xpath(Competitions.Search.COUNTRIES)
        clubs = self.get_list_by_xpath(Competitions.Search.CLUBS)
        players = self.get_list_by_xpath(Competitions.Search.PLAYERS)
        total_market_value = self.get_list_by_xpath(Competitions.Search.TOTAL_MARKET_VALUES)
        mean_market_value = self.get_list_by_xpath(Competitions.Search.MEAN_MARKET_VALUES)
        continent = self.get_list_by_xpath(Competitions.Search.CONTINENTS)

        results.append({
            "id": extract_from_url(url),
            "name": name[0] if name else None,
            "country": country[0] if country else None,
            "clubs": clubs[0] if clubs else None,
            "players": players[0] if players else None,
            "totalMarketValue": total_market_value[0] if total_market_value else None,
            "meanMarketValue": mean_market_value[0] if mean_market_value else None,
            "continent": continent[0] if continent else None,
        })

    return results