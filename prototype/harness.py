import argparse
import json
import pathlib
import re
import sys

import boto3
import pandas as pd

MODULORDNER = pathlib.Path(__file__).resolve().parent
PROJEKTORDNER = MODULORDNER.parent
sys.path.insert(0, str(MODULORDNER))

from scoring import GEWICHTE, SCHWELLE_STABIL, UMGEBUNGEN, bewerte, lade_hilfsdaten

REGION = "eu-central-1"
STANDARD_MODELL = "qwen.qwen3-coder-30b-a3b-v1:0"

FALLDATEI = MODULORDNER / "lokalisationspruefung.jsonl"
LABELDATEI = PROJEKTORDNER / "export_kpis" / "dataset_mit_labels.csv"
ROHDATENDATEI = PROJEKTORDNER / "export_kpis" / "dataset.jsonl"

ANNOTATIONSKOPF = re.compile(r"^\s*#\s*(Project|Layer|Source|Antipattern|Hinweis):")
QUELLE = re.compile(r"^\s*#\s*Source:\s*(.+)$", re.MULTILINE)
ANNOTATIONSMARKE = re.compile(r"MUTATED|#\s*FEHLER", re.IGNORECASE)
TEURER_AUFRUF = re.compile(
    r"session|execute|query|commit|fetch|requests\.|http|sleep\(", re.IGNORECASE
)
AUFRUFMUSTER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*\(")
SCHLEIFENMUSTER = re.compile(r"\b(for|while)\b")

PUNKTE_AUFRUF = 3
PUNKTE_TEURER_AUFRUF = 2
PUNKTE_AWAIT = 1
PUNKTE_IN_SCHLEIFE = 2

MARKE_FEHLER = re.compile(r"#\s*FEHLER", re.IGNORECASE)
NAEHE = 5

KLASSEN = {
    "1": "Query DB (N+1, redundante oder fehlende Abfragen)",
    "2": "CPU (unnötige CPU-Arbeit)",
    "3": "Blocking/Contention (blockierende Aufrufe, Sperren)",
    "4": "Speicher/Datenvolumen (zu viel geladen oder gehalten)",
    "5": "I/O Chatty (viele kleine Schreibvorgänge)",
}

KLASSENZUORDNUNG = {
    ("P01", "002"): "1",
    ("P06", "052"): "1",
    ("P09", "069"): "4",
    ("P01", "010"): "2",
    ("P01", "011"): "2",
    ("P10", "079"): "2",
    ("P11", "088"): "2",
    ("P01", "008"): "3",
    ("P01", "012"): "3",
    ("P01", "019"): "3",
    ("P04", "032"): "3",
    ("P05", "035"): "4",
    ("P09", "072"): "4",
    ("P11", "086"): "4",
    ("P06", "048"): "5",
    ("P07", "058"): "5",
}


def bereinigte_zeilennummern(rohtext):
    zeilen = rohtext.splitlines()
    behalten = [
        index
        for index, zeile in enumerate(zeilen)
        if not ANNOTATIONSKOPF.match(zeile) and not ANNOTATIONSMARKE.search(zeile)
    ]
    while behalten and not zeilen[behalten[0]].strip():
        behalten.pop(0)
    while behalten and not zeilen[behalten[-1]].strip():
        behalten.pop()
    return {roh: nummer for nummer, roh in enumerate(behalten, start=1)}


def kernzeilen(rohtext):
    zeilen = rohtext.splitlines()
    zuordnung = bereinigte_zeilennummern(rohtext)
    treffer = set()
    for index, zeile in enumerate(zeilen):
        if not MARKE_FEHLER.search(zeile):
            continue
        for folge in range(index + 1, len(zeilen)):
            kandidat = zeilen[folge].strip()
            if kandidat and not kandidat.startswith("#"):
                if folge in zuordnung:
                    treffer.add(zuordnung[folge])
                break
    return sorted(treffer)


def normalisiere_zeile(text):
    if not isinstance(text, str):
        return ""
    ohne_nummer = re.sub(r"^\s*\d+\s*[|:]\s*", "", text.strip())
    return " ".join(ohne_nummer.split())


def bewerte_zeile(genannt, fall, zitat=None):
    kern = fall.get("kernzeilen") or []
    if not isinstance(genannt, int):
        genannt = None
    abstand = min((abs(genannt - k) for k in kern), default=None) if genannt else None
    in_region = genannt in fall["geaenderte_zeilen"] if genannt else False

    zitat_sauber = normalisiere_zeile(zitat)
    zeilen_sauber = {
        nummer: normalisiere_zeile(text)
        for nummer, text in enumerate(fall["snippet"].splitlines(), start=1)
    }
    zitat_exakt = bool(zitat_sauber) and any(
        zitat_sauber == zeilen_sauber.get(k, "") for k in kern
    )
    zitat_region = bool(zitat_sauber) and any(
        zitat_sauber == zeilen_sauber.get(n, "") for n in fall["geaenderte_zeilen"]
    )
    return {
        "zeile": genannt,
        "abstand": abstand,
        "exakt": abstand == 0,
        "nah": abstand is not None and abstand <= NAEHE,
        "region_weit": bool(in_region),
        "exakt_zitat": zitat_exakt,
        "region_zitat": zitat_region,
        "kernzeilen": kern,
    }


def ohne_annotation(text):
    bleibt = []
    for zeile in text.splitlines():
        if ANNOTATIONSKOPF.match(zeile):
            continue
        if ANNOTATIONSMARKE.search(zeile):
            continue
        bleibt.append(zeile)
    return "\n".join(bleibt).strip("\n")


def quelle(text):
    treffer = QUELLE.search(text)
    return treffer.group(1).strip() if treffer else ""


def antipattern_angabe(text):
    for zeile in text.splitlines():
        if zeile.startswith("#") and "Antipattern" in zeile:
            return zeile.split(":", 1)[1].strip()
    return ""


def mit_zeilennummern(text, nur_geaenderte=None):
    zeilen = text.splitlines()
    auswahl = range(1, len(zeilen) + 1) if nur_geaenderte is None else nur_geaenderte
    return "\n".join(
        f"{nummer:>4} | {'+' if nur_geaenderte is not None else ' '} {zeilen[nummer - 1]}"
        for nummer in auswahl
    )


SYSTEM_PROMPT = """Du bist ein KI-Agent zur Bewertung der Stabilität von Code-Änderungen. Du erhältst die gemessenen Kennzahlen einer Änderung, den Vergleich mit der Referenz derselben Methode und Umgebungsstufe sowie den Ausschnitt des geänderten Codes mit nummerierten Zeilen. Bewerte und erkläre nach den folgenden Regeln.

1. Den Punktwert und die Punkte je Kriterium übernimmst du aus der übergebenen Berechnung. Erfinde oder schätze keine Zahlen.
2. Vergleiche ausschließlich mit der Referenz derselben Methode und Umgebungsstufe.
3. Benenne als Hauptursache genau das Kriterium mit dem größten Punktverlust und belege es mit den Zahlen. Erkläre den Punktwert außerdem anhand der Beiträge der Kriterien, also Punkte mal Gewicht.
4. Wenn die Fehlerquote auffällt, führe sie als Lastphänomen auf, nicht als Fehler der Änderung.
5. Nenne genau eine Codezeile als Ursache, und zwar eine, die im übergebenen Ausschnitt steht. Gib dazu die Zeilennummer und den vollständigen Wortlaut dieser Zeile an. Wählst du Fehlerklasse 0, lass `codestelle` leer.
6. Ordne die Änderung genau einer Fehlerklasse zu. Erlaubt sind ausschließlich diese Nummern: 0 = kein Fehler erkennbar, 1 = Query DB (N+1, redundante oder fehlende Abfragen), 2 = CPU (unnötige CPU-Arbeit), 3 = Blocking/Contention (blockierende Aufrufe in asynchronem Code, Sperren), 4 = Speicher/Datenvolumen (zu viel geladen oder gehalten, fehlende Obergrenze, Slicing im Speicher), 5 = I/O Chatty (viele kleine Schreibvorgänge). Wähle 0, wenn der Ausschnitt keine Auffälligkeit zeigt; erfinde keinen Fehler.

Vorgehen: Analysiere zuerst in zwei bis drei Sätzen, welcher Mechanismus den gemessenen Effekt erklärt. Prüfe dabei, welche Zeilen gegenüber dem unveränderten Code neu sind, und benenne die Zeile, die diesen Mechanismus trägt. Gib erst danach das JSON aus:

{"score_prozent": ..., "kriterien": [{"name": ..., "abweichung_prozent": ..., "punkte": ..., "gewicht": ...}], "modell_wahrscheinlichkeit": ..., "fehlerklasse": "<1 bis 5>", "einstufung": ..., "hauptursache": ..., "codestelle": {"datei": ..., "zeile": ..., "zitat": "..."}, "empfehlung": ..., "hinweise": ...}"""


def lade_rohdaten():
    index = {}
    for zeile in (json.loads(z) for z in open(ROHDATENDATEI, encoding="utf-8")):
        index[(zeile["variant"], zeile["method"], zeile["env"])] = zeile
    return index


def baue_faelle():
    daten = pd.read_csv(LABELDATEI, dtype={"nummer": str})
    daten["projekt"] = daten["variante"].str.replace("_neg", "", regex=False)
    rohdaten = lade_rohdaten()
    faelle = []
    for (projekt, nummer), gruppe in daten.groupby(["projekt", "nummer"]):
        gesund = gruppe[gruppe["label_kpi"] == 0]
        mutiert = gruppe[gruppe["label_kpi"] == 1]
        if gesund.empty or mutiert.empty:
            continue
        text_gesund = ohne_annotation(gesund["snippet"].iloc[0])
        text_mutiert = ohne_annotation(mutiert["snippet"].iloc[0])
        if text_gesund == text_mutiert:
            continue
        metadaten = rohdaten.get(
            (
                mutiert["variante"].iloc[0],
                mutiert["methode"].iloc[0],
                mutiert["umgebung"].iloc[0],
            ),
            {},
        )
        gesund_zeilen = set(text_gesund.splitlines())
        alle = [(i + 1, z) for i, z in enumerate(text_mutiert.splitlines())]
        kern = metadaten.get("kernzeilen", [])
        geaendert = sorted({n for n, t in alle if t not in gesund_zeilen} | set(kern))
        if not geaendert:
            continue
        faelle.append(
            {
                "projekt": projekt,
                "nummer": nummer,
                "methode": gruppe["methode"].iloc[0],
                "datei": metadaten.get("quelle", ""),
                "variante_negativ": mutiert["variante"].iloc[0],
                "ziel_kriterium": mutiert["ziel_kriterium"].iloc[0],
                "snippet": text_mutiert,
                "snippet_original": text_gesund,
                "geaenderte_zeilen": geaendert,
                "kernzeilen": kern,
                "antipattern_dokumentiert": metadaten.get("antipattern", ""),
                "fehlerklasse": KLASSENZUORDNUNG.get((projekt, nummer), "unbekannt"),
                "zeilen_gesamt": len(alle),
            }
        )
    with open(FALLDATEI, "w", encoding="utf-8") as fh:
        for fall in faelle:
            fh.write(json.dumps(fall, ensure_ascii=False) + "\n")
    return faelle


def lade_faelle():
    if not FALLDATEI.exists():
        return baue_faelle()
    return [json.loads(zeile) for zeile in open(FALLDATEI, encoding="utf-8")]


def finde_fall(nummer):
    for fall in lade_faelle():
        if fall["nummer"].zfill(3) == str(nummer).zfill(3):
            return fall
    raise SystemExit(f"Kein Fall mit Nummer {nummer}")


def berechnung_fuer(methode, umgebung, negativ=True):
    referenz, notgrenzen = lade_hilfsdaten()
    for zeile in (json.loads(z) for z in open(ROHDATENDATEI, encoding="utf-8")):
        if zeile["method"] != methode or zeile["env"] != umgebung:
            continue
        ist_negativ = zeile["variant"].endswith("_neg")
        if ist_negativ == negativ:
            messung = {
                "target_method": zeile["method"],
                "env": zeile["env"],
                **zeile["metrics"],
            }
            return bewerte(messung, referenz, notgrenzen)
    art = "Negativmessung" if negativ else "Positivmessung"
    raise SystemExit(f"Keine {art} für {methode} in {umgebung}")


def verdacht(zeilen, index):
    text = zeilen[index][1]
    wert = 0.0
    if AUFRUFMUSTER.search(text):
        wert += PUNKTE_AUFRUF
    if TEURER_AUFRUF.search(text):
        wert += PUNKTE_TEURER_AUFRUF
    if "await" in text:
        wert += PUNKTE_AWAIT
    einzug = len(text) - len(text.lstrip())
    for vorher in range(index - 1, -1, -1):
        ober = zeilen[vorher][1]
        if not ober.strip():
            continue
        if (len(ober) - len(ober.lstrip())) < einzug:
            if SCHLEIFENMUSTER.search(ober):
                wert += PUNKTE_IN_SCHLEIFE
            break
    return wert


def basislinie(ansicht="voll"):
    zeilen = []
    for fall in lade_faelle():
        alle_zeilen = [(i + 1, z) for i, z in enumerate(fall["snippet"].splitlines())]
        geaendert = set(fall["geaenderte_zeilen"])
        if ansicht == "diff":
            alle = [(n, t) for n, t in alle_zeilen if n in geaendert]
        else:
            alle = alle_zeilen
        kandidaten = [n for n, t in alle if t.strip()]
        zufall_top1 = len(geaendert & set(kandidaten)) / len(kandidaten)
        bewertet = sorted(
            (
                (verdacht(alle, i), n)
                for i, (n, _) in enumerate(alle)
                if alle[i][1].strip()
            ),
            key=lambda p: (-p[0], p[1]),
        )
        top1 = bewertet[0][1] if bewertet else None
        top3 = {n for _, n in bewertet[:3]}
        pruefung = bewerte_zeile(top1, fall)
        zeilen.append(
            {
                "Fall": f"{fall['projekt']}/{fall['nummer']}",
                "geaendert": len(geaendert),
                "Zeilen": len(alle),
                "Top-1 Zeile": top1,
                "Kernzeilen": pruefung["kernzeilen"],
                "Abstand": pruefung["abstand"],
                "exakt": pruefung["exakt"],
                "nah (<=5)": pruefung["nah"],
                "Region weit": pruefung["region_weit"],
                "Top-3 Region": bool(top3 & geaendert),
                "Zufall Top-1": round(zufall_top1, 3),
                "Zufall Top-3": round(1 - (1 - zufall_top1) ** 3, 3),
            }
        )
    return pd.DataFrame(zeilen)


def umgebungsuebersicht(methode, negativ=True):
    uebersicht = []
    for umgebung in UMGEBUNGEN:
        try:
            ergebnis = berechnung_fuer(methode, umgebung, negativ)
        except SystemExit:
            continue
        uebersicht.append(
            {
                "umgebungsstufe": umgebung,
                "punktwert": ergebnis["score_prozent"],
                "einstufung": ergebnis["einstufung"],
                "hauptursache": ergebnis["hauptursache"],
            }
        )
    return uebersicht


def score_erklaerung(methode, umgebung, berechnung, negativ=True):
    return {
        "methode": methode,
        "umgebungsstufe": umgebung,
        "formel": (
            "Punktwert = Summe aus Punkte x Gewicht "
            f"(Durchsatz {kommazahl(GEWICHTE['requests_per_sec'])}, "
            f"p95-Latenz {kommazahl(GEWICHTE['p95_latency_ms'])}, "
            f"mittlere Latenz {kommazahl(GEWICHTE['avg_latency_ms'])})"
        ),
        "kriterien": [
            {
                "kriterium": k["name"],
                "gewicht": k["gewicht"],
                "punkte": k["punkte"],
                "beitrag_zum_punktwert": round(k["punkte"] * k["gewicht"], 2),
                "abweichung_prozent": k["abweichung_prozent"],
            }
            for k in berechnung["kriterien"]
        ],
        "punktwert": berechnung["score_prozent"],
        "einstufung": berechnung["einstufung"],
        "hinweise": berechnung["hinweise"],
        "umgebungen": umgebungsuebersicht(methode, negativ),
    }


def anzeigeentscheidung(berechnung, klasse=None, zeile=None):
    if berechnung["score_prozent"] >= SCHWELLE_STABIL:
        hinweis = None
        if klasse and str(klasse) != "0":
            hinweis = (
                "KPI-Werte und Stabilitätsscore sind hoch; der Agent vermutet einen Fehler "
                f"bei Zeile {zeile}, die Messung bestätigt ihn jedoch nicht."
            )
        return {
            "anzeige": "keine Auffälligkeit gemessen",
            "fehlerklasse_angezeigt": False,
            "qualifizierter_hinweis": hinweis,
        }
    return {
        "anzeige": f"Auffälligkeit bestätigt: {berechnung['hauptursache']}",
        "fehlerklasse_angezeigt": True,
        "qualifizierter_hinweis": None,
    }


def baue_nachricht(fall, berechnung, ansicht="voll", snippet=None):
    ausschnittstext = fall["snippet"] if snippet is None else snippet
    if ansicht == "diff":
        ausschnitt = mit_zeilennummern(ausschnittstext, fall["geaenderte_zeilen"])
        hinweis = "Der Ausschnitt zeigt ausschließlich die gegenüber dem unveränderten Code neuen Zeilen."
    else:
        ausschnitt = mit_zeilennummern(ausschnittstext)
        hinweis = (
            "Der Ausschnitt zeigt die vollständige Methode; nicht alle Zeilen sind neu."
        )
    return json.dumps(
        {
            "methode": fall["methode"],
            "datei": fall.get("datei", ""),
            "umgebungsstufe": berechnung["umgebung"],
            "gemessene_werte": berechnung["messwerte"],
            "berechnete_bewertung": {
                "score_prozent": berechnung["score_prozent"],
                "einstufung": berechnung["einstufung"],
                "kriterien": berechnung["kriterien"],
                "hauptursache": berechnung["hauptursache"],
                "rechenweg": [
                    {
                        "kriterium": k["name"],
                        "gewicht": k["gewicht"],
                        "punkte": k["punkte"],
                        "beitrag_zum_punktwert": round(k["punkte"] * k["gewicht"], 2),
                    }
                    for k in berechnung["kriterien"]
                ],
                "hinweise": berechnung["hinweise"],
            },
            "aenderungsausschnitt_mit_zeilennummern": ausschnitt,
            "hinweis_zum_ausschnitt": hinweis,
        },
        ensure_ascii=False,
        indent=2,
    )


def pruefe_zahlen(antwort, berechnung):
    gleich = antwort.get("score_prozent") == berechnung["score_prozent"]
    return {
        "gueltig": bool(gleich),
        "score_gemeldet": antwort.get("score_prozent"),
        "score_erwartet": berechnung["score_prozent"],
    }


def als_zahl(wert):
    if isinstance(wert, str) and wert.strip().isdigit():
        return int(wert.strip())
    return wert if isinstance(wert, int) else None


def kommazahl(wert):
    return f"{wert:.2f}".replace(".", ",")


def json_aus_text(text):
    bereinigt = text.strip()
    if bereinigt.startswith("```"):
        bereinigt = bereinigt.split("```")[1]
        if bereinigt.startswith("json"):
            bereinigt = bereinigt[4:]
    start = bereinigt.find("{")
    if start < 0:
        return None
    tiefe = 0
    for position in range(start, len(bereinigt)):
        zeichen = bereinigt[position]
        if zeichen == "{":
            tiefe += 1
        elif zeichen == "}":
            tiefe -= 1
            if tiefe == 0:
                try:
                    return json.loads(bereinigt[start : position + 1])
                except json.JSONDecodeError:
                    return None
    return None


def rufe_modell(nachricht, modell, max_tokens, temperatur=0.0):
    client = boto3.client("bedrock-runtime", region_name=REGION)
    koerper = {
        "messages": [{"role": "user", "content": SYSTEM_PROMPT + "\n\n" + nachricht}],
        "max_tokens": max_tokens,
        "temperature": temperatur,
    }
    antwort = client.invoke_model(modelId=modell, body=json.dumps(koerper))
    inhalt = json.loads(antwort["body"].read())
    return inhalt["choices"][0]["message"]["content"], inhalt.get("usage", {})


def lauf(
    modell,
    umgebung,
    max_tokens,
    ansicht="voll",
    wiederholungen=1,
    kontrolle=False,
):
    faelle = lade_faelle()
    verteilung = {}
    for fall in faelle:
        verteilung[fall["fehlerklasse"]] = verteilung.get(fall["fehlerklasse"], 0) + 1
    mehrheitsklasse = max(verteilung.values()) / len(faelle)

    zeilen = []
    for fall in faelle:
        if kontrolle:
            berechnung = berechnung_fuer(fall["methode"], umgebung, negativ=False)
            nachricht = baue_nachricht(
                fall, berechnung, "voll", snippet=fall["snippet_original"]
            )
            erwartet = "0"
        else:
            berechnung = berechnung_fuer(fall["methode"], umgebung)
            nachricht = baue_nachricht(fall, berechnung, ansicht)
            erwartet = fall["fehlerklasse"]
        for runde in range(1, wiederholungen + 1):
            text, nutzung = rufe_modell(nachricht, modell, max_tokens)
            antwort = json_aus_text(text)
            if antwort is None:
                zahlen = {"gueltig": False}
                genannt, zit, klasse = None, None, None
            else:
                zahlen = pruefe_zahlen(antwort, berechnung)
                stelle = antwort.get("codestelle") or {}
                genannt = als_zahl(stelle.get("zeile"))
                zit = stelle.get("zitat")
                klasse = str(antwort.get("fehlerklasse", "")).strip()
            pruefung = bewerte_zeile(genannt, fall, zit)
            zeilen.append(
                {
                    "Fall": f"{fall['projekt']}/{fall['nummer']}",
                    "Runde": runde,
                    "Klasse": klasse,
                    "erwartet": erwartet,
                    "Klasse Treffer": klasse == erwartet,
                    "genannt": pruefung["zeile"],
                    "Abstand": pruefung["abstand"],
                    "exakt Nr.": pruefung["exakt"],
                    "nah Nr.": pruefung["nah"],
                    "exakt Zitat": pruefung["exakt_zitat"],
                    "JSON": antwort is not None,
                    "Zahlen": zahlen["gueltig"],
                    "Eingabe": nutzung.get("prompt_tokens"),
                    "Ausgabe": nutzung.get("completion_tokens"),
                }
            )
    tabelle = pd.DataFrame(zeilen)
    print(
        f"Ansicht: {ansicht} | Wiederholungen: {wiederholungen} | Fälle je Runde: {len(faelle)}"
    )
    print()
    print(tabelle.to_string(index=False))
    print()
    for spalte in ["Klasse Treffer", "exakt Nr.", "nah Nr.", "exakt Zitat"]:
        print(
            f"{spalte:18s}",
            round(tabelle[spalte].mean(), 3),
            f"({int(tabelle[spalte].sum())} von {len(tabelle)})",
        )
    print("JSON gültig:      ", round(tabelle["JSON"].mean(), 3))
    print("Zahlen übernommen:", round(tabelle["Zahlen"].mean(), 3))
    print()
    print(
        "Bezugsgrößen Fehlerklasse: Mehrheitsklasse",
        round(mehrheitsklasse, 3),
        "| Zufall bei fünf Klassen 0,200",
    )
    print()
    if wiederholungen > 1:
        print("Streuung über die Wiederholungen (Mittel je Runde):")
        for spalte in ["Klasse Treffer", "exakt Nr.", "nah Nr."]:
            werte = tabelle.groupby("Runde")[spalte].mean()
            print(
                f"  {spalte:18s} {round(werte.mean(), 3)} +/- {round(werte.std(), 3)}"
            )
        print()
    gesamt_eingabe = int(tabelle["Eingabe"].sum())
    gesamt_ausgabe = int(tabelle["Ausgabe"].sum())
    print(
        "Token gesamt: Eingabe",
        gesamt_eingabe,
        "| Ausgabe",
        gesamt_ausgabe,
        "| Aufrufe:",
        len(tabelle),
    )
    return tabelle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bauen", action="store_true")
    parser.add_argument("--basislinie", action="store_true")
    parser.add_argument("--lauf", action="store_true")
    parser.add_argument("--modell", default=STANDARD_MODELL)
    parser.add_argument("--max-tokens", type=int, default=1500)
    parser.add_argument("--ansicht", choices=["voll", "diff"], default="voll")
    parser.add_argument("--wiederholungen", type=int, default=1)
    parser.add_argument("--kontrolle", action="store_true")
    parser.add_argument("--erklaerung", action="store_true")
    parser.add_argument("--nummer")
    parser.add_argument("--umgebung")
    parser.add_argument("--antwort")
    args = parser.parse_args()

    if args.lauf:
        if not args.umgebung:
            raise SystemExit("--umgebung erforderlich für --lauf (z. B. extreme)")
        lauf(
            args.modell,
            args.umgebung,
            args.max_tokens,
            args.ansicht,
            args.wiederholungen,
            args.kontrolle,
        )
        return

    if args.erklaerung:
        if not args.nummer or not args.umgebung:
            raise SystemExit("--nummer und --umgebung erforderlich für --erklaerung")
        fall = finde_fall(args.nummer)
        berechnung = berechnung_fuer(fall["methode"], args.umgebung)
        erklaerung = score_erklaerung(fall["methode"], args.umgebung, berechnung)
        erklaerung["anzeige"] = anzeigeentscheidung(
            berechnung, fall["fehlerklasse"], (fall["kernzeilen"] or [None])[0]
        )
        print(json.dumps(erklaerung, ensure_ascii=False, indent=2))
        return

    if args.bauen:
        faelle = baue_faelle()
        print("Fälle:", len(faelle), "-> gespeichert in", FALLDATEI.name)
        for fall in faelle:
            print(
                f"  {fall['projekt']}/{fall['nummer']} {fall['methode'][:32]:32s} geänderte Zeilen {fall['geaenderte_zeilen']}"
            )
        return

    if args.basislinie:
        tabelle = basislinie(args.ansicht)
        print(f"Ansicht: {args.ansicht}")
        print(tabelle.to_string(index=False))
        print()
        print(
            "Mittel:",
            tabelle[
                ["exakt", "nah (<=5)", "Region weit", "Top-3 Region", "Zufall Top-1"]
            ]
            .mean()
            .round(3)
            .to_dict(),
        )
        return

    if not args.nummer or not args.umgebung:
        raise SystemExit(
            "--nummer und --umgebung erforderlich (oder --bauen / --basislinie)"
        )

    fall = finde_fall(args.nummer)
    berechnung = berechnung_fuer(fall["methode"], args.umgebung)

    if args.antwort is None:
        print("### System-Prompt\n")
        print(SYSTEM_PROMPT)
        print("\n### Nutzernachricht\n")
        print(baue_nachricht(fall, berechnung))
        print("\n### Ground Truth")
        print(
            "Geänderte Zeilen:", fall["geaenderte_zeilen"], "von", fall["zeilen_gesamt"]
        )
        return

    antwort = json.loads(args.antwort)
    print(
        "Zahlenprüfung:",
        json.dumps(pruefe_zahlen(antwort, berechnung), ensure_ascii=False),
    )
    stelle = antwort.get("codestelle") or {}
    pruefung = bewerte_zeile(als_zahl(stelle.get("zeile")), fall, stelle.get("zitat"))
    print(
        "Lokalisation:  ",
        json.dumps(
            {"geaenderte_zeilen": fall["geaenderte_zeilen"], **pruefung},
            ensure_ascii=False,
        ),
    )


if __name__ == "__main__":
    main()
