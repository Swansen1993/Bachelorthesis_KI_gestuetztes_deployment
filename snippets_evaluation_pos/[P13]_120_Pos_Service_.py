# Project: P13_transfermarkt-api
# Layer: Business Logic (Service)
# Source: app/services/players/transfers.py

from dataclasses import dataclass
from app.services.base import TransfermarktBase
from app.utils.utils import safe_split
from app.utils.xpath import Players

@dataclass
class TransfermarktPlayerTransfers(TransfermarktBase):
    player_id: str = None

    def get_player_transfers(self) -> dict:
        self.response["id"] = self.player_id
        self.response["transfers"] = self._parse_player_transfer_history()
        self.response["youthClubs"] = safe_split(self.get_text_by_xpath(Players.Transfers.YOUTH_CLUBS), ",")
        return self.response