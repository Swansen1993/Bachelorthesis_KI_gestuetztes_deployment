# Project: P13_transfermarkt-api
# Layer: Business Logic (Service)
# Source: app/services/clubs/profile.py

from dataclasses import dataclass
from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_COUNTRY_ID
from app.utils.utils import extract_from_url, safe_regex
from app.utils.xpath import Clubs

@dataclass
class TransfermarktClubProfile(TransfermarktBase):
    club_id: str = None

    def get_club_profile(self) -> dict:
        self.response["id"] = self.club_id
        self.response["url"] = self.get_text_by_xpath(Clubs.Profile.URL)
        self.response["name"] = self.get_text_by_xpath(Clubs.Profile.NAME)
        self.response["officialName"] = self.get_text_by_xpath(Clubs.Profile.NAME_OFFICIAL)
        self.response["squad"] = {
            "size": self.get_text_by_xpath(Clubs.Profile.SQUAD_SIZE),
            "averageAge": self.get_text_by_xpath(Clubs.Profile.SQUAD_AVG_AGE),
        }
        self.response["league"] = {
            "id": extract_from_url(self.get_text_by_xpath(Clubs.Profile.LEAGUE_ID)),
            "name": self.get_text_by_xpath(Clubs.Profile.LEAGUE_NAME),
            "countryId": safe_regex(self.get_text_by_xpath(Clubs.Profile.LEAGUE_COUNTRY_ID), REGEX_COUNTRY_ID, "id"),
        }
        return self.response