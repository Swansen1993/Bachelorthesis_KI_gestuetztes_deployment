# Project: P13_transfermarkt-api
# Layer: Business Logic (Service)
# Source: app/services/players/stats.py

from dataclasses import dataclass
from app.services.base import TransfermarktBase

@dataclass
class TransfermarktPlayerStats(TransfermarktBase):
    player_id: str = None

    def get_player_stats(self) -> dict:
        self.response["id"] = self.player_id
        self.response["stats"] = self._parse_player_stats()
        return self.response