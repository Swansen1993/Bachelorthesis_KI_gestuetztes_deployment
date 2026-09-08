import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"

ROUTES = [
    ("ceapi/marketValueDevelopment", "mv_graph.json", "json"),
    ("ceapi/transferHistory", "transfers.json", "json"),
    ("/marktwertverlauf/spieler", "player_market_value.html", "html"),
    ("/transfers/spieler", "player_transfers.html", "html"),
    ("/leistungsdatendetails/spieler", "player_stats.html", "html"),
    ("/profil/spieler", "player_profile.html", "html"),
    ("/datenfakten/verein", "club_profile.html", "html"),
    ("/startseite/wettbewerb", "competition_clubs.html", "html"),
    ("/schnellsuche", "search.html", "html"),
]


class _FixtureResponse:
    def __init__(self, content: bytes):
        self.content = content
        self.status_code = 200
        self.reason = "OK"

    def json(self):
        return json.loads(self.content)

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


def replay(url: str) -> _FixtureResponse:
    for needle, filename, kind in ROUTES:
        if needle in url:
            path = FIXTURES_DIR / filename
            if not path.exists():
                raise FileNotFoundError(f"Fixture fehlt: {path}")
            content = path.read_bytes()
            if kind == "json":
                return _FixtureResponse(content)
            return _FixtureResponse(content)
    raise FileNotFoundError(f"Kein Fixture für URL: {url}")
