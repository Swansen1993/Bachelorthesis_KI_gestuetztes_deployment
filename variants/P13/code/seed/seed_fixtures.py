import os
from pathlib import Path

FIXTURES_DIR = Path("/app/fixtures")
ZIELDATEI = FIXTURES_DIR / "player_stats.html"
ANZAHL = int(os.getenv("SEED_ROWS", "1"))


def datenzeilen(rumpf):
    zeilen = []
    rest = rumpf
    while "<tr>" in rest:
        start = rest.index("<tr>")
        ende = rest.index("</tr>", start) + len("</tr>")
        zeilen.append(rest[start:ende])
        rest = rest[ende:]
    return zeilen


def main():
    text = ZIELDATEI.read_text(encoding="utf-8")
    koerper_start = text.index("<tbody>") + len("<tbody>")
    koerper_ende = text.index("</tbody>")
    zeilen = datenzeilen(text[koerper_start:koerper_ende])

    if not zeilen:
        raise SystemExit("Keine Datenzeile in player_stats.html gefunden")

    if ANZAHL <= len(zeilen):
        print(f"Datenzeilen bereits ausreichend: {len(zeilen)}")
        return

    zusatz = ("\n" + zeilen[0]) * (ANZAHL - len(zeilen))
    ZIELDATEI.write_text(
        text[:koerper_ende] + zusatz + text[koerper_ende:], encoding="utf-8"
    )
    print(f"Datenzeilen ergaenzt: {ANZAHL - len(zeilen)}")


main()
