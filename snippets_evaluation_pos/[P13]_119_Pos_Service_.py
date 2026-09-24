# Project: P13_transfermarkt-api
# Layer: Business Logic (Service)
# Source: app/services/players/market_value.py

from dataclasses import dataclass
from app.services.base import TransfermarktBase
from app.utils.utils import zip_lists_into_dict
from app.utils.xpath import Players

@dataclass
class TransfermarktPlayerMarketValue(TransfermarktBase):
    player_id: str = None

    def get_player_market_value(self) -> dict:
        self.response["id"] = self.player_id
        self.response["marketValue"] = self.get_text_by_xpath(Players.MarketValue.CURRENT, join_str="")
        self.response["marketValueHistory"] = self._parse_market_value_history()
        self.response["ranking"] = zip_lists_into_dict(
            self.get_list_by_xpath(Players.MarketValue.RANKINGS_NAMES),
            self.get_list_by_xpath(Players.MarketValue.RANKINGS_POSITIONS),
        )
        return self.response