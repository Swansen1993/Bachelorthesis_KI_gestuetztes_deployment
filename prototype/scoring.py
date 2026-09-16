import argparse
import json
import pathlib

import pandas as pd

MODULORDNER = pathlib.Path(__file__).resolve().parent
PROJEKTORDNER = MODULORDNER.parent
KPI_CSV_ORDNER = PROJEKTORDNER / "export_kpis" / "csv_kpis"

PUNKTE_BESTE = 100
PUNKTE_BEI_FEHLENDER_REFERENZ = 40
SCHWELLE_STABIL = 75
SCHWELLE_GRENZFALL = 50

GEWICHTE = {
    "requests_per_sec": 0.40,
    "p95_latency_ms": 0.35,
    "avg_latency_ms": 0.25,
}
KRITERIUMNAME = {
    "requests_per_sec": "Durchsatz gegenüber Referenz",
    "p95_latency_ms": "p95-Latenz gegenüber Referenz",
    "avg_latency_ms": "Mittlere Latenz gegenüber Referenz",
}
BAENDER_DURCHSATZ = [(10, PUNKTE_BESTE), (30, 80), (60, 50)]
BAENDER_LATENZ = [(20, PUNKTE_BESTE), (40, 80), (60, 50)]
MINDESTABWEICHUNG_MS = 3.0
UMGEBUNGEN = ("low", "medium", "high", "extreme", "prod")


def punkte_aus_baendern(prozentwert, baender):
    for grenze, punkte in baender:
        if prozentwert <= grenze:
            return punkte
    return 0


def punkte_durchsatz(verlust_prozent):
    return punkte_aus_baendern(verlust_prozent, BAENDER_DURCHSATZ)


def punkte_latenz(anstieg_prozent):
    return punkte_aus_baendern(anstieg_prozent, BAENDER_LATENZ)


def einstufung(score_prozent):
    if score_prozent >= SCHWELLE_STABIL:
        return "stabil"
    if score_prozent >= SCHWELLE_GRENZFALL:
        return "Grenzfall"
    return "instabil"


def lade_hilfsdaten():
    referenz = pd.read_csv(MODULORDNER / "referenzwerte.csv")
    notgrenzen = pd.read_csv(MODULORDNER / "notgrenzen.csv")
    return referenz, notgrenzen


def finde_messung(methode, umgebung, negativ):
    datei = sorted(KPI_CSV_ORDNER.glob("all_projects_kpis_[0-9]*.csv"))[-1]
    df = pd.read_csv(datei)
    df["is_neg"] = df["variant"].str.endswith("_neg").astype(int)
    treffer = df[
        (df["target_method"] == methode)
        & (df["env"] == umgebung)
        & (df["is_neg"] == int(negativ))
    ]
    if treffer.empty:
        raise SystemExit(
            f"Keine Messung gefunden: {methode} / {umgebung} / negativ={negativ}"
        )
    return treffer.iloc[0], datei.name


def bewerte(messung, referenz, notgrenzen):
    zeile_referenz = referenz[
        (referenz["target_method"] == messung["target_method"])
        & (referenz["env"] == messung["env"])
    ]
    grenzen = notgrenzen[notgrenzen["env"] == messung["env"]]

    kriterien = []
    hinweise = []

    if not zeile_referenz.empty:
        bezug = zeile_referenz.iloc[0]
        abweichungen = {
            spalte: (messung[spalte] - bezug[spalte]) / bezug[spalte] * 100
            for spalte in GEWICHTE
        }
        zuwachs = {spalte: messung[spalte] - bezug[spalte] for spalte in GEWICHTE}
        punkte = {
            "requests_per_sec": punkte_durchsatz(-abweichungen["requests_per_sec"]),
            "p95_latency_ms": punkte_latenz(abweichungen["p95_latency_ms"]),
            "avg_latency_ms": punkte_latenz(abweichungen["avg_latency_ms"]),
        }
        for spalte in ("p95_latency_ms", "avg_latency_ms"):
            if zuwachs[spalte] < MINDESTABWEICHUNG_MS:
                punkte[spalte] = PUNKTE_BESTE
                hinweise.append(
                    f"{KRITERIUMNAME[spalte]}: Anstieg unter "
                    f"{MINDESTABWEICHUNG_MS} ms, daher als unauffällig bewertet."
                )
        for spalte in GEWICHTE:
            kriterien.append(
                {
                    "name": KRITERIUMNAME[spalte],
                    "abweichung_prozent": round(abweichungen[spalte], 1),
                    "punkte": punkte[spalte],
                    "gewicht": GEWICHTE[spalte],
                }
            )
    else:
        hinweise.append(
            "Keine Referenz für diese Methode und Umgebungsstufe: Bewertung über Notgrenzen, geringere Aussagekraft."
        )
        g = grenzen.iloc[0]
        punkte = {
            "requests_per_sec": (
                PUNKTE_BESTE
                if messung["requests_per_sec"] >= g["durchsatz_unten"]
                else PUNKTE_BEI_FEHLENDER_REFERENZ
            ),
            "p95_latency_ms": (
                PUNKTE_BESTE
                if messung["p95_latency_ms"] <= g["p95_oben"]
                else PUNKTE_BEI_FEHLENDER_REFERENZ
            ),
            "avg_latency_ms": (
                PUNKTE_BESTE
                if messung["avg_latency_ms"] <= g["avg_oben"]
                else PUNKTE_BEI_FEHLENDER_REFERENZ
            ),
        }
        for spalte in GEWICHTE:
            kriterien.append(
                {
                    "name": KRITERIUMNAME[spalte],
                    "abweichung_prozent": None,
                    "punkte": punkte[spalte],
                    "gewicht": GEWICHTE[spalte],
                }
            )

    score_prozent = round(sum(k["punkte"] * k["gewicht"] for k in kriterien))

    verluste = sorted(
        (
            (
                k["gewicht"] * (100 - k["punkte"]),
                k["name"],
                k["punkte"],
                k["abweichung_prozent"],
            )
            for k in kriterien
        ),
        reverse=True,
    )
    if verluste[0][0] > 0:
        hauptursache = f"{verluste[0][1]} (Punkte {verluste[0][2]}, Abweichung {verluste[0][3]} Prozent)"
    else:
        hauptursache = "Kein Kriterium unter der Bestnote"

    return {
        "methode": messung["target_method"],
        "umgebung": messung["env"],
        "messwerte": {spalte: round(float(messung[spalte]), 2) for spalte in GEWICHTE},
        "kriterien": kriterien,
        "score_prozent": score_prozent,
        "einstufung": einstufung(score_prozent),
        "hauptursache": hauptursache,
        "hinweise": hinweise,
    }


def pruefe(antwort, messung, referenz, notgrenzen):
    neu = bewerte(messung, referenz, notgrenzen)
    stimmt = neu["score_prozent"] == antwort["score_prozent"]
    return {
        "gueltig": bool(stimmt),
        "score_nachgerechnet": neu["score_prozent"],
        "score_gemeldet": antwort["score_prozent"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--methode", required=True)
    parser.add_argument("--umgebung", required=True)
    parser.add_argument("--negativ", action="store_true")
    args = parser.parse_args()

    referenz, notgrenzen = lade_hilfsdaten()
    messung, quellname = finde_messung(args.methode, args.umgebung, args.negativ)
    antwort = bewerte(messung, referenz, notgrenzen)

    print("Quelldatei:", quellname)
    print(json.dumps(antwort, indent=2, ensure_ascii=False))
    print()
    print(
        "Prüfschicht:",
        json.dumps(pruefe(antwort, messung, referenz, notgrenzen), ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
