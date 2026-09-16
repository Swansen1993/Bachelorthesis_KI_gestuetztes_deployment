from dataclasses import dataclass

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Competitions


@dataclass
class TransfermarktCompetitionSearch(TransfermarktBase):
    """
    A class for searching football competitions on Transfermarkt and retrieving search results.

    Args:
        query (str): The search query for finding football clubs.
        URL (str): The URL template for the search query.
        page_number (int): The page number of search results (default is 1).
    """

    query: str = None
    URL: str = (
        "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}&Wettbewerb_page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self) -> None:
        """Initialize the TransfermarktCompetitionSearch class."""
        self.URL = self.URL.format(query=self.query, page_number=self.page_number)
        self.page = self.request_url_page()

    def __parse_search_results(self) -> list:
        """
        Parse and retrieve the search results for football competitions from Transfermarkt.

        Returns:
            list: A list of dictionaries, each containing details of a football competition,
                including its unique identifier, name, country, associated clubs, number of players,
                total market value, mean market value, and continent.
        """
        urls = self.get_list_by_xpath(Competitions.Search.URLS)
        results = []

        for url in urls:
            name = self.get_list_by_xpath(Competitions.Search.NAMES)
            country = self.get_list_by_xpath(Competitions.Search.COUNTRIES)
            clubs = self.get_list_by_xpath(Competitions.Search.CLUBS)
            players = self.get_list_by_xpath(Competitions.Search.PLAYERS)
            total_market_value = self.get_list_by_xpath(
                Competitions.Search.TOTAL_MARKET_VALUES
            )
            mean_market_value = self.get_list_by_xpath(
                Competitions.Search.MEAN_MARKET_VALUES
            )
            continent = self.get_list_by_xpath(Competitions.Search.CONTINENTS)

            results.append(
                {
                    "id": extract_from_url(url),
                    "name": name[0] if name else None,
                    "country": country[0] if country else None,
                    "clubs": clubs[0] if clubs else None,
                    "players": players[0] if players else None,
                    "totalMarketValue": total_market_value[0]
                    if total_market_value
                    else None,
                    "meanMarketValue": mean_market_value[0]
                    if mean_market_value
                    else None,
                    "continent": continent[0] if continent else None,
                }
            )

        return results

    def search_competitions(self) -> dict:
        """
        Perform a search for football competitions and retrieve the search results.

        Returns:
            dict: A dictionary containing search results, including competition details.
        """
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_last_page_number(Competitions.Search.BASE)
        self.response["results"] = self.__parse_search_results()

        return self.response
