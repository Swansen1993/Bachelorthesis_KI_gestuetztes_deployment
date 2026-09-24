import argparse
import datetime
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import export_kpis_to_csv as kpi_export

PROJEKTORDNER = pathlib.Path(__file__).resolve().parent.parent
PROTOKOLLORDNER = PROJEKTORDNER / "prototype"
PROTOKOLLFELD = "modellvorhersage"
PROTOKOLLMUSTER = re.compile(r"\d{4}-\d{2}-\d{2}_\d{4}")
STEMPELMUSTER = re.compile(r"(\d{4}-\d{2}-\d{2}_\d{4})")
STAND_DATEI = PROJEKTORDNER / "export_kpis" / "_import_stand.json"


def hole_messungen():
    dump = pathlib.Path(tempfile.mkdtemp(prefix="kpi_import_"))
    try:
        kpi_export._sync_bucket(dump, None)
        daten = pd.DataFrame(kpi_export._collect_rows(dump), columns=kpi_export.COLUMNS)
    finally:
        shutil.rmtree(dump, ignore_errors=True)
    daten["env"] = pd.Categorical(
        daten["env"], categories=kpi_export.ENV_ORDER, ordered=True
    )
    return daten.sort_values(["variant", "messung", "target_method", "env"]).reset_index(
        drop=True
    )


def schreibe_csv(daten):
    kpi_export.OUT_DIR.mkdir(parents=True, exist_ok=True)
    zeitstempel = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zieldatei = kpi_export.OUT_DIR / f"all_projects_kpis_{zeitstempel}.csv"
    daten.to_csv(zieldatei, index=False)
    daten.to_csv(kpi_export.OUT_DIR / "all_projects_kpis_new.csv", index=False)
    return zieldatei


def zeige_stand(daten):
    print(
        "Zeilen:",
        len(daten),
        "| Varianten:",
        daten["variant"].nunique(),
        "| Messungen:",
        daten["messung"].nunique(),
    )
    print()
    print("Neueste Messung je Variante (Umgebungsstufen):")
    for variante in sorted(daten["variant"].unique()):
        teil = daten[daten["variant"] == variante]
        messung = sorted(teil["messung"].unique())[-1]
        stufen = teil.loc[teil["messung"] == messung, "env"].nunique()
        haken = "ok" if stufen == len(kpi_export.ENV_ORDER) else "unvollständig"
        print(f"  {variante:12s} {messung:22s} {stufen} Stufen {haken}")
    print()
    print("Zeilen je Messung (letzte 10):")
    print(daten["messung"].value_counts().sort_index().tail(10).to_string())


def ist_protokoll(pfad):
    with open(pfad, encoding="utf-8") as datei:
        erste = datei.readline()
    if not erste.strip():
        return False
    try:
        zeile = json.loads(erste)
    except json.JSONDecodeError:
        return False
    return isinstance(zeile, dict) and PROTOKOLLFELD in zeile


def zielname(datei):
    if PROTOKOLLMUSTER.search(datei.name):
        return datei.name
    stempel = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    return f"{stempel}_{datei.name}"


def uebernimm_protokolle(quelle):
    quelle = pathlib.Path(quelle)
    dateien = [quelle] if quelle.is_file() else sorted(quelle.glob("*.jsonl"))
    if not dateien:
        print("Keine Protokolldateien gefunden in", quelle)
        return
    for datei in dateien:
        if not ist_protokoll(datei):
            print("  übersprungen (kein Protokoll):", datei.name)
            continue
        ziel = PROTOKOLLORDNER / zielname(datei)
        shutil.copyfile(datei, ziel)
        print("  übernommen:", ziel)


def hole_protokolle_aus_bucket():
    zielordner = pathlib.Path(tempfile.mkdtemp(prefix="protokoll_import_"))
    kpi_export._run_aws(
        [
            "s3",
            "sync",
            f"s3://{kpi_export.BUCKET}/protokolle/",
            str(zielordner),
            "--exclude",
            "*",
            "--include",
            "*.jsonl",
        ]
    )
    return zielordner


def rufe_aws(argumente):
    ergebnis = subprocess.run(
        ["aws", "--region", kpi_export.REGION, *argumente],
        check=True,
        capture_output=True,
        text=True,
    )
    return ergebnis.stdout


def protokoll_stempel():
    ausgabe = rufe_aws(["s3", "ls", f"s3://{kpi_export.BUCKET}/protokolle/"])
    return {treffer.group(1) for treffer in STEMPELMUSTER.finditer(ausgabe)}


def importiere(stempel):
    if not stempel:
        return
    print()
    print("Neue Läufe:", ", ".join(sorted(stempel)))
    daten = hole_messungen()
    print("KPI-CSV geschrieben:", schreibe_csv(daten))
    quelle = hole_protokolle_aus_bucket()
    try:
        uebernimm_protokolle(quelle)
    finally:
        shutil.rmtree(quelle, ignore_errors=True)


def lade_stand():
    if STAND_DATEI.exists():
        return set(json.loads(STAND_DATEI.read_text(encoding="utf-8")))
    return set()


def speichere_stand(stempel):
    STAND_DATEI.write_text(
        json.dumps(sorted(stempel), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def neue_stempel():
    vorhanden = protokoll_stempel()
    if not STAND_DATEI.exists():
        speichere_stand(vorhanden)
        print("Erster Lauf: vorhandene Stempel als Ausgangsstand gespeichert.")
        return set(), vorhanden
    stand = lade_stand()
    return vorhanden - stand, stand


def pruefe_einmal():
    neu, stand = neue_stempel()
    if not neu:
        print("Kein neuer Lauf.")
        return
    importiere(neu)
    speichere_stand(stand | neu)


def beobachte(intervall):
    neu, stand = neue_stempel()
    for stempel in sorted(neu):
        importiere(stempel)
    speichere_stand(stand | neu)
    print("Beobachter läuft (Intervall", intervall, "s). Abbruch mit Strg+C.")
    try:
        while True:
            time.sleep(intervall)
            try:
                jetzt = protokoll_stempel()
            except subprocess.CalledProcessError as fehler:
                print("Bucket-Abruf fehlgeschlagen:", fehler)
                continue
            neu = jetzt - stand
            if neu:
                importiere(neu)
                stand |= neu
                speichere_stand(stand)
            if not neu:
                print(f"kein neuer Lauf ({len(stand)} Stempel bekannt)")
    except KeyboardInterrupt:
        print()
        print("Beobachter beendet.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protokolle", help="Datei oder Ordner mit Harness-Protokollen (*.jsonl)"
    )
    parser.add_argument(
        "--protokolle-s3",
        action="store_true",
        help="Protokolle aus dem Bucket (Ordner protokolle/) übernehmen",
    )
    parser.add_argument(
        "--beobachten",
        type=int,
        metavar="SEKUNDEN",
        help="Bucket beobachten und je neuem Lauf einmal importieren",
    )
    parser.add_argument(
        "--pruefen",
        action="store_true",
        help="einmal nach neuen Läufen sehen, ggf. importieren, beenden",
    )
    args = parser.parse_args()

    if args.beobachten:
        beobachte(args.beobachten)
        return

    if args.pruefen:
        pruefe_einmal()
        return

    daten = hole_messungen()
    zieldatei = schreibe_csv(daten)
    print("KPI-CSV geschrieben:", zieldatei)
    print()
    zeige_stand(daten)

    if args.protokolle:
        print()
        print("Protokolle übernehmen:")
        uebernimm_protokolle(args.protokolle)

    if args.protokolle_s3:
        print()
        print("Protokolle aus dem Bucket übernehmen:")
        quelle = hole_protokolle_aus_bucket()
        try:
            uebernimm_protokolle(quelle)
        finally:
            shutil.rmtree(quelle, ignore_errors=True)

    print()
    print("Fertig.")


if __name__ == "__main__":
    main()
