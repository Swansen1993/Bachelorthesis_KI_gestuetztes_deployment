# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O Parser
# Source: app/services/players/profile.py

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url, trim
from app.utils.xpath import Players

def parse_player_relatives(self: TransfermarktBase) -> list:
    relatives = self.page.xpath(Players.Profile.RELATIVES)
    result = []
    for relative in relatives:
        url = trim(relative.xpath(Players.Profile.RELATIVE_URL))
        name = trim(relative.xpath(Players.Profile.RELATIVE_NAME))
        result.append(
            {
                "id": extract_from_url(url),
                "url": url,
                "name": name,
                "profileType": "player" if "spieler" in url else "trainer",
            },
        )
    return result