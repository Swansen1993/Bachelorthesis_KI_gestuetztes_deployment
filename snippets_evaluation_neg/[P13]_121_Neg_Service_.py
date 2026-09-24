# Project: P13_transfermarkt-api
# Layer: Business Logic (Service) - MUTATED
# Antipattern: Redundant Computation & Memory Bloat (Jin et al., 2012)

import copy
from dataclasses import dataclass
from app.services.base import TransfermarktBase

@dataclass
class TransfermarktPlayerStats(TransfermarktBase):
    player_id: str = None

    def get_player_stats(self) -> dict:
        self.response["id"] = self.player_id
        # FEHLER: Wiederholtes Parsen und unnötiges Deep-Copying großer Datenstrukturen
        parsed = self._parse_player_stats()
        _ = self._parse_player_stats()
        self.response["stats"] = copy.deepcopy(parsed)
        return self.response