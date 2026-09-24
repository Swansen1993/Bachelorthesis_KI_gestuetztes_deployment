import pathlib

import pandas as pd

MODULORDNER = pathlib.Path(__file__).resolve().parent
PROJEKTORDNER = MODULORDNER.parent
KPI_CSV_ORDNER = PROJEKTORDNER / "export_kpis" / "csv_kpis"

TRAININGSPROJEKTE = [
    "P01",
    "P02",
    "P04",
    "P05",
    "P06",
    "P07",
    "P08",
    "P09",
    "P10",
    "P11",
]
EVALUATIONSPROJEKTE = ["P12", "P13"]
MESSGROESSEN = ["requests_per_sec", "p95_latency_ms", "avg_latency_ms"]


def lade_kpi():
    datei = sorted(KPI_CSV_ORDNER.glob("all_projects_kpis_[0-9]*.csv"))[-1]
    df = pd.read_csv(datei)
    df["is_neg"] = df["variant"].str.endswith("_neg").astype(int)
    df["project_id"] = df["variant"].str.replace("_neg", "", regex=False)
    return df, datei.name


def baue_referenztabelle(df, projekte=TRAININGSPROJEKTE, zielname="referenzwerte.csv"):
    gesund = df[(df["is_neg"] == 0) & df["project_id"].isin(projekte)]
    referenz = (
        gesund.groupby(["target_method", "env"])[MESSGROESSEN].median().reset_index()
    )
    ziel = MODULORDNER / zielname
    referenz.to_csv(ziel, index=False)
    return referenz, ziel


def baue_notgrenzen(df, projekte=TRAININGSPROJEKTE, zielname="notgrenzen.csv"):
    gesund = df[(df["is_neg"] == 0) & df["project_id"].isin(projekte)]
    notgrenzen = pd.DataFrame(
        {
            "durchsatz_unten": gesund.groupby("env")["requests_per_sec"].quantile(0.10),
            "avg_oben": gesund.groupby("env")["avg_latency_ms"].quantile(0.90),
            "p95_oben": gesund.groupby("env")["p95_latency_ms"].quantile(0.90),
        }
    ).reset_index()
    ziel = MODULORDNER / zielname
    notgrenzen.to_csv(ziel, index=False)
    return notgrenzen, ziel


GRUPPEN = (
    ("Training", TRAININGSPROJEKTE, "referenzwerte.csv", "notgrenzen.csv"),
    (
        "Evaluation",
        EVALUATIONSPROJEKTE,
        "referenzwerte_evaluation.csv",
        "notgrenzen_evaluation.csv",
    ),
)


if __name__ == "__main__":
    df, quellname = lade_kpi()
    print("Quelldatei:", quellname)
    for bezeichnung, projekte, referenzdatei, notgrenzendatei in GRUPPEN:
        referenz, referenzziel = baue_referenztabelle(df, projekte, referenzdatei)
        notgrenzen, notgrenzenziel = baue_notgrenzen(df, projekte, notgrenzendatei)
        print()
        print(f"--- {bezeichnung} ({', '.join(projekte)}) ---")
        print(
            "Referenzzeilen (Methode x Umgebung):",
            len(referenz),
            "->",
            referenzziel.name,
        )
        print("Methoden:", referenz["target_method"].nunique())
