import pathlib
from functools import lru_cache

import numpy as np
import pandas as pd
import shap
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

ROOT = pathlib.Path(__file__).resolve().parent.parent
MERKMALE = ["avg_latency_ms", "p95_latency_ms", "requests_per_sec"]
BEZEICHNUNGEN = {
    "avg_latency_ms": "Mittlere Latenz",
    "p95_latency_ms": "p95-Latenz",
    "requests_per_sec": "Durchsatz",
}
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
GRENZFAELLE = ["_029_", "_041_", "_046_", "_056_", "_063_"]
ZUFALL = 42
SCHWELLE = 0.027


def lade_analysesatz(verzeichnis=None):
    ordner = (
        pathlib.Path(verzeichnis) if verzeichnis else ROOT / "export_kpis" / "csv_kpis"
    )
    datei = sorted(ordner.glob("all_projects_kpis_[0-9]*.csv"))[-1]
    daten = pd.read_csv(datei)
    daten["is_neg"] = daten["variant"].str.endswith("_neg").astype(int)
    daten["project_id"] = daten["variant"].str.replace("_neg", "", regex=False)
    daten = daten[daten["project_id"].isin(TRAININGSPROJEKTE)]
    grenzfaelle = (daten["is_neg"] == 1) & daten["target_method"].str.contains(
        "|".join(GRENZFAELLE)
    )
    return daten[~grenzfaelle]


def vorbereitung():
    return ColumnTransformer(
        transformers=[
            (
                "log",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        (
                            "log",
                            FunctionTransformer(
                                np.log1p, feature_names_out="one-to-one"
                            ),
                        ),
                        ("scaler", StandardScaler()),
                    ]
                ),
                MERKMALE,
            )
        ],
        sparse_threshold=0.0,
        verbose_feature_names_out=False,
    )


def lgbm_klassifikator():
    return LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=7,
        min_child_samples=20,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        random_state=ZUFALL,
        verbose=-1,
    )


def lade_kpi_modell(daten=None):
    daten = lade_analysesatz() if daten is None else daten
    kpi_modell = Pipeline(
        steps=[("prep", vorbereitung()), ("clf", lgbm_klassifikator())]
    )
    kpi_modell.fit(daten[MERKMALE], daten["is_neg"])
    return kpi_modell, shap.TreeExplainer(kpi_modell.named_steps["clf"])


@lru_cache(maxsize=1)
def _standard():
    return lade_kpi_modell()


def _beitraege(erklaerer, vorbereitet):
    werte = erklaerer.shap_values(vorbereitet)
    if isinstance(werte, list):
        werte = werte[1]
    elif getattr(werte, "ndim", 2) == 3:
        werte = werte[:, :, 1]
    return np.ravel(np.asarray(werte))


def erklaere_kpi(messung, daten=None):
    fehlend = [merkmal for merkmal in MERKMALE if messung.get(merkmal) is None]
    if fehlend:
        return {"hinweis": "Kennzahlen fehlen: " + ", ".join(fehlend)}
    kpi_modell, erklaerer = lade_kpi_modell(daten) if daten is not None else _standard()
    zeile = pd.DataFrame([{merkmal: messung[merkmal] for merkmal in MERKMALE}])
    vorbereitet = kpi_modell.named_steps["prep"].transform(zeile)
    werte = _beitraege(erklaerer, vorbereitet)
    wahrscheinlichkeit = float(kpi_modell.predict_proba(zeile)[0, 1])
    ausgangswert = float(np.ravel(erklaerer.expected_value)[-1])
    summe = float(kpi_modell.named_steps["clf"].predict(vorbereitet, raw_score=True)[0])
    return {
        "wahrscheinlichkeit_mutiert_prozent": round(wahrscheinlichkeit * 100, 1),
        "urteil": "instabil" if wahrscheinlichkeit >= SCHWELLE else "nicht instabil",
        "entscheidungsgrenze_prozent": round(SCHWELLE * 100, 1),
        "ausgangswert": round(ausgangswert, 3),
        "summe": round(summe, 3),
        "beitraege": [
            {
                "merkmal": BEZEICHNUNGEN[merkmal],
                "beitrag": round(float(wert), 3),
                "spricht_fuer": "instabil" if wert > 0 else "nicht instabil",
            }
            for merkmal, wert in zip(MERKMALE, werte)
        ],
        "summe_stimmt": bool(abs(ausgangswert + float(werte.sum()) - summe) < 1e-9),
    }
