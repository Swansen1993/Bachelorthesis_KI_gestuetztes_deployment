# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O Parser - MUTATED
# Antipattern: Uncoordinated Functions / Repeated XPath Traversals (Jin et al., 2012)

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url, to_camel_case, zip_lists_into_dict
from app.utils.xpath import Players

def parse_player_stats(self: TransfermarktBase) -> list:
    rows = self.page.xpath(Players.Stats.ROWS)
    data = []

    # FEHLER: Wiederholte Abfrage der globalen Header- und URL-Listen in jedem Schleifendurchlauf
    for row in rows:
        headers = to_camel_case(
            ["Competition id", "Club id", "Season id", "Competition name"]
            + self.get_list_by_xpath(Players.Stats.HEADERS),
        )
        competitions_urls = self.get_list_by_xpath(Players.Stats.COMPETITIONS_URLS)
        clubs_urls = self.get_list_by_xpath(Players.Stats.CLUBS_URLS)
        
        stat_item = [item for text in row.xpath(Players.Stats.DATA) if text != "\xa0" for item in text.split("\xa0/\xa0")][1:]
        
        comp_id = extract_from_url(competitions_urls[0]) if competitions_urls else ""
        club_id = extract_from_url(clubs_urls[0]) if clubs_urls else ""
        
        row_data = [comp_id, club_id] + stat_item
        data.append(zip_lists_into_dict(headers, row_data))

    return data