import os
from pathlib import Path

FIXTURES_DIR = Path("/app/fixtures")
STATS_DATEI = FIXTURES_DIR / "player_stats.html"
SEARCH_DATEI = FIXTURES_DIR / "search.html"


def datenzeilen(rumpf):
    zeilen = []
    rest = rumpf
    while "<tr" in rest:
        start = rest.index("<tr")
        ende = rest.index("</tr>", start) + len("</tr>")
        zeilen.append(rest[start:ende])
        rest = rest[ende:]
    return zeilen


def stats_koerper(text):
    start = text.index("<tbody>") + len("<tbody>")
    return start, text.index("</tbody>", start)


def search_koerper(text):
    marke = text.index("<h2>competitions</h2>")
    start = text.index("<tbody>", marke) + len("<tbody>")
    return start, text.index("</tbody>", start)


def erweitere(datei, anzahl, koerper):
    text = datei.read_text(encoding="utf-8")
    start, ende = koerper(text)
    zeilen = datenzeilen(text[start:ende])

    if not zeilen:
        raise SystemExit(f"Keine Datenzeile in {datei.name} gefunden")

    if anzahl <= len(zeilen):
        print(f"{datei.name}: Datenzeilen bereits ausreichend: {len(zeilen)}")
        return

    zusatz = ("\n" + zeilen[0]) * (anzahl - len(zeilen))
    datei.write_text(text[:ende] + zusatz + text[ende:], encoding="utf-8")
    print(f"{datei.name}: Datenzeilen ergaenzt: {anzahl - len(zeilen)}")


def main():
    erweitere(STATS_DATEI, int(os.getenv("SEED_ROWS", "1")), stats_koerper)
    erweitere(SEARCH_DATEI, int(os.getenv("SEED_SEARCH_ROWS", "1")), search_koerper)


main()
