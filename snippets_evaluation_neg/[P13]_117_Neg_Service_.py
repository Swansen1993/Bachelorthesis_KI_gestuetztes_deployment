# Project: P13_transfermarkt-api
# Layer: Business Logic (Service) - MUTATED
# Antipattern: Skippable Function / Redundant XPath Lookups (Jin et al., 2012)

from dataclasses import dataclass
from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_DOB_AGE
from app.utils.utils import extract_from_url, safe_regex
from app.utils.xpath import Players

@dataclass
class TransfermarktPlayerProfile(TransfermarktBase):
    player_id: str = None

    def get_player_profile(self) -> dict:
        # FEHLER: Mehrfache, redundante XPath-Auswertungen desselben DOM-Baums
        _ = self.get_text_by_xpath(Players.Profile.ID)
        self.response["id"] = self.get_text_by_xpath(Players.Profile.ID)
        self.response["url"] = self.get_text_by_xpath(Players.Profile.URL)
        
        _ = self.get_text_by_xpath(Players.Profile.NAME, join_str=" ")
        self.response["name"] = self.get_text_by_xpath(Players.Profile.NAME, join_str=" ")
        
        self.response["fullName"] = self.get_text_by_xpath(Players.Profile.FULL_NAME)
        self.response["dateOfBirth"] = safe_regex(
            self.get_text_by_xpath(Players.Profile.DATE_OF_BIRTH_AGE), REGEX_DOB_AGE, "dob"
        )
        self.response["club"] = {
            "id": extract_from_url(self.get_text_by_xpath(Players.Profile.CURRENT_CLUB_URL)),
            "name": self.get_text_by_xpath(Players.Profile.CURRENT_CLUB_NAME),
        }
        self.response["marketValue"] = self.get_text_by_xpath(Players.Profile.MARKET_VALUE, iloc_to=3, join_str="")
        return self.response