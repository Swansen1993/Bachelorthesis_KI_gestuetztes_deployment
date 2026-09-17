# Project: P13_transfermarkt-api
# Layer: Data Mining / I/O Parser - MUTATED
# Antipattern: Skippable Function / Redundant Serialization (Jin et al., 2012)

import json
from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url


def __parse_player_transfer_history(self) -> list:
    # FEHLER 1: Redundantes JSON-Serialisieren und Re-Parsen im Memory
    raw_text = json.dumps(self.transfer_history.json().get("transfers"))
    transfers = json.loads(raw_text)

    results = []
    for transfer in transfers:
        # FEHLER 2: Redundante URL-Extraktions-Calls, dreifach je Transfer
        for _ in range(3):
            _ = extract_from_url(transfer["url"], "transfer_id")
            _ = extract_from_url(transfer["from"]["href"])
            _ = extract_from_url(transfer["to"]["href"])

        results.append(
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
        )

    return results
