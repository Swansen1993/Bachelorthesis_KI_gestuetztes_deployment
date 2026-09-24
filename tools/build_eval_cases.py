import json
import pathlib
import sys

ROOT = pathlib.Path(
    "/Users/svenniederlohner/projects/Bachelorthesis_KI_gestuetztes_deployment"
)
sys.path.insert(0, str(ROOT / "prototype"))

from harness import (
    antipattern_angabe,
    bewerte,
    lade_hilfsdaten,
    ohne_annotation,
    quelle,
)

ROHDATEN = ROOT / "export_kpis" / "dataset.jsonl"
FALLDATEI = ROOT / "prototype" / "lokalisationspruefung.jsonl"
KURZNAMEN = {
    "Durchsatz gegenüber Referenz": "durchsatz",
    "p95-Latenz gegenüber Referenz": "p95_latenz",
    "Mittlere Latenz gegenüber Referenz": "mittlere_latenz",
}


def baue_eval_faelle():
    referenz, notgrenzen = lade_hilfsdaten()
    zeilen = [json.loads(z) for z in open(ROHDATEN, encoding="utf-8")]
    eval_zeilen = [z for z in zeilen if z["split"] == "eval"]

    gruppen = {}
    for zeile in eval_zeilen:
        schluessel = (zeile["variant"].replace("_neg", ""), zeile["pos"])
        gruppen.setdefault(schluessel, {})[zeile["label"]] = zeile

    faelle = []
    for (projekt, nummer), gruppe in sorted(gruppen.items()):
        gesund = gruppe.get(0)
        mutiert = gruppe.get(1)
        if gesund is None or mutiert is None:
            continue
        if not gesund["snippet"] or not mutiert["snippet"]:
            continue

        text_gesund = ohne_annotation(gesund["snippet"])
        text_mutiert = ohne_annotation(mutiert["snippet"])
        if text_gesund == text_mutiert:
            continue

        kern = mutiert["kernzeilen"]
        gesund_zeilen = set(text_gesund.splitlines())
        alle = [(i + 1, z) for i, z in enumerate(text_mutiert.splitlines())]
        geaendert = sorted({n for n, t in alle if t not in gesund_zeilen} | set(kern))
        if not geaendert:
            continue

        messung = {
            "target_method": mutiert["method"],
            "env": mutiert["env"],
            "variante": mutiert["variant"],
            **mutiert["metrics"],
        }
        antwort = bewerte(messung, referenz, notgrenzen)
        verluste = sorted(
            (
                (k["gewicht"] * (100 - k["punkte"]), KURZNAMEN[k["name"]])
                for k in antwort["kriterien"]
            ),
            reverse=True,
        )

        faelle.append(
            {
                "projekt": projekt,
                "nummer": nummer,
                "methode": mutiert["method"],
                "datei": quelle(mutiert["snippet"]),
                "variante_negativ": mutiert["variant"],
                "ziel_kriterium": verluste[0][1] if verluste[0][0] > 0 else "keines",
                "snippet": text_mutiert,
                "snippet_original": text_gesund,
                "geaenderte_zeilen": geaendert,
                "kernzeilen": kern,
                "antipattern_dokumentiert": antipattern_angabe(mutiert["snippet"]),
                "zeilen_gesamt": len(alle),
            }
        )
    return faelle


def main():
    faelle = baue_eval_faelle()
    vorhanden = (
        [json.loads(z) for z in open(FALLDATEI, encoding="utf-8")]
        if FALLDATEI.exists()
        else []
    )
    bekannt = {(f["projekt"], f["nummer"]) for f in vorhanden}
    neu = [f for f in faelle if (f["projekt"], f["nummer"]) not in bekannt]

    with open(FALLDATEI, "a", encoding="utf-8") as fh:
        for fall in neu:
            fh.write(json.dumps(fall, ensure_ascii=False) + "\n")

    print(
        f"Angehaengt: {len(neu)}"
        f" | bereits vorhanden: {len(faelle) - len(neu)}"
        f" | Faelle in der Falldatei: {len(vorhanden) + len(neu)}"
    )


if __name__ == "__main__":
    main()
