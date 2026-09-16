# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O Parser
# Source: app/services/players/stats.py

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url, to_camel_case, zip_lists_into_dict
from app.utils.xpath import Players

def parse_player_stats(self: TransfermarktBase) -> list:
    rows = self.page.xpath(Players.Stats.ROWS)
    headers = to_camel_case(
        ["Competition id", "Club id", "Season id", "Competition name"]
        + self.get_list_by_xpath(Players.Stats.HEADERS),
    )
    competitions_urls = self.get_list_by_xpath(Players.Stats.COMPETITIONS_URLS)
    clubs_urls = self.get_list_by_xpath(Players.Stats.CLUBS_URLS)
    competitions_ids = [extract_from_url(url) for url in competitions_urls]
    clubs_ids = [extract_from_url(url) for url in clubs_urls]
    stats = [
        [item for text in row.xpath(Players.Stats.DATA) if text != "\xa0" for item in text.split("\xa0/\xa0")][1:]
        for row in rows
    ]
    data = [
        [comp_url, club_url] + stats for comp_url, club_url, stats in list(zip(competitions_ids, clubs_ids, stats))
    ]
    return [zip_lists_into_dict(headers, stat) for stat in data]