# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O Parser
# Source: app/services/players/transfers.py

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url

def parse_player_transfer_history(self: TransfermarktBase) -> list:
    transfers = self.transfer_history.json().get("transfers")

    return [
        {
            "id": extract_from_url(transfer["url"], "transfer_id"),
            "clubFrom": {
                "id": extract_from_url(transfer["from"]["href"]),
                "name": transfer["from"]["clubName"],
            },
            "clubTo": {
                "id": extract_from_url(transfer["to"]["href"]),
                "name": transfer["to"]["clubName"],
            },
            "date": transfer["date"],
            "upcoming": transfer["upcoming"],
            "season": transfer["season"],
            "marketValue": transfer["marketValue"],
            "fee": transfer["fee"],
        }
        for transfer in transfers
    ]