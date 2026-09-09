# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O Parser
# Source: app/services/clubs/search.py

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Clubs

def parse_search_results(self: TransfermarktBase) -> list:
    clubs_names = self.get_list_by_xpath(Clubs.Search.NAMES)
    clubs_urls = self.get_list_by_xpath(Clubs.Search.URLS)
    clubs_countries = self.get_list_by_xpath(Clubs.Search.COUNTRIES)
    clubs_squads = self.get_list_by_xpath(Clubs.Search.SQUADS)
    clubs_market_values = self.get_list_by_xpath(Clubs.Search.MARKET_VALUES)
    clubs_ids = [extract_from_url(url) for url in clubs_urls]

    return [
        {
            "id": idx,
            "url": url,
            "name": name,
            "country": country,
            "squad": squad,
            "marketValue": market_value,
        }
        for idx, url, name, country, squad, market_value in zip(
            clubs_ids,
            clubs_urls,
            clubs_names,
            clubs_countries,
            clubs_squads,
            clubs_market_values,
        )
    ]