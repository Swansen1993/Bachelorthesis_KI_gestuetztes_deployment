# ML-Notizen & Quellen – Positiv/Negativ-Klassifikator

Lokale, nicht versionierte Datei (gitignored via `/ml/QUELLEN.md`).
Enthält **Erklärungen & Begründungen** (für die Verschriftlichung) **und** die zugehörigen **Quellen** je Code-Schritt.

## Erklärungen & Begründungen

### Warum LightGBM als Modell?

Der Pos/Neg-Unterschied zeigt sich in **nichtlinearen KPI-Mustern und Feature-Interaktionen** (z. B. „hohe Fehlerquote erst zusammen mit hoher Latenz = verdächtig"). Begründung für LightGBM (Gradient Boosting auf Entscheidungsbäumen):

- **Tabellendaten:** KPI-Spalten + kategoriale Umgebung sind klassische Tabellendaten – dort sind Tree-Ensembles state of the art.
- **Nichtlinearität:** Bäume modellieren Schwellen/Stufen („Fehlerquote > 8 % UND Latenz > 500 ms"), keine linearen Grenzen wie LogReg.
- **Interaktionen:** Verschachtelte Abfragen lernen Wechselwirkungen zwischen Features automatisch.
- **Keine Skalierung nötig / robust:** Entscheidungen über Schwellenwerte statt Abstände → unempfindlich gegen Ausreißer (z. B. hängengebliebene Läufe).
- **Erklärbar via SHAP:** `TreeExplainer` liefert exakte, schnelle Feature-Beiträge → keine Blackbox.
- **Abgrenzung:** LogReg = einfache, erklärbare **Baseline** (linearer Anker zum Vergleich); Random Forest (Bagging) meist etwas schwächer als Boosting; XGBoost ähnlich, LightGBM schneller/leichtgewichtiger; Deep Learning bräuchte deutlich mehr Daten und ist schwerer erklärbar.
- **Risiko/Overfitting:** Bei kleinen Daten kann Boosting overfitten → Gegenmaßnahmen: `class_weight="balanced"`, begrenzte Komplexität, **strikter Split nach Projekt** (held-out P12/P13), um Generalisierung nachzuweisen.

### Weitere Entscheidungen (laufend ergänzen)

**Direkt echter Datenpfad statt Mock (Design-Entscheidung, 2026-09-08):**
- Das Notebook lädt **direkt die echte KPI-CSV** (`export_kpis/all_projects_kpis_new.csv`) – kein synthetischer Mock-Datensatz.
- Begründung: Die Negativ-Läufe (32 Läufe) sind voraussichtlich fertig, bevor das Notebook fertiggestellt ist → kein doppelter Code (Mock + echt) nötig.
- **Schutz/Guard:** Eine Zelle prüft, ob `*_neg`-Zeilen (Negativ-Läufe) in der CSV vorhanden sind. Fehlen sie, bricht das Notebook mit einem klaren Hinweis ab – es läuft nie still mit unvollständigen Daten weiter.
- **Label-Logik** hängt am `_neg`-Suffix der Spalte `variant`; `base_project` wird per `str.replace("_neg", "")` abgeleitet.
- **`variant`/`target_method` sind bewusst KEINE Features** (nur Gruppen/IDs) → keine Leakage, Generalisierung auf neue Projekte (P12/P13 held-out).
- **Data-Cleaning** (eigene Zelle, sobald finale Läufe vorliegen): Problemläufe filtern (z. B. P07-Läufe mit 100 % Fehlern durch Seed-Bug, `P01_legacy`-Altbestand), NaN-Behandlung (Imputer eingeplant).
- **Trainings-/Evaluations-Split:** Training = **P01–P11** (Nutzerentscheid 2026-09-08: P01 wird verwendet), Evaluation (held-out) = P12/P13. `variant`/`target_method` sind keine Features → Generalisierung auf unbekannte Projekte.
- **Offen/anzupassen:** Sobald die finale CSV mit der echten Negativ-Kampagnen-Verteilung (32 Läufe) vorliegt, wird `TRAINING_PROJECTS` an die tatsächlich vorhandenen Positiv/Negativ-Projekte angeglichen (Absprache 2026-09-08).
- **Weitere geplante Schritte:** GroupShuffleSplit nach Projekt (gegen Leakage), Preprocessing nur auf Train gefittet, LogReg (Baseline) → LightGBM, Metriken F1/PR-AUC/Confusion, SHAP.

## Notebook: posneg_klassifikator.ipynb

### Daten laden & Manipulation (pandas)
- pandas `read_csv`: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- pandas `DataFrame`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html

### Zufall & Arrays (numpy)
- numpy `random` (default_rng): https://numpy.org/doc/stable/reference/random/generator.html

### Modellauswahl & Splits (scikit-learn)
- scikit-learn – Modellauswahl/Splits: https://scikit-learn.org/stable/modules/model_selection.html
- `GroupShuffleSplit`: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html

### Preprocessing (scikit-learn)
- `SimpleImputer`: https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html
- `StandardScaler`: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
- `OneHotEncoder`: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html
- `ColumnTransformer`: https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html
- `Pipeline`: https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html

### Modell
- Gradient Boosting (Konzept, Ensemble-Methoden): https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting
- `LogisticRegression`: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- LightGBM Python API (`LGBMClassifier`): https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.LGBMClassifier.html

### Metriken (scikit-learn)
- scikit-learn – Metriken: https://scikit-learn.org/stable/modules/model_evaluation.html
- `confusion_matrix`: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
- `f1_score`: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html
- `precision_recall_curve`: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html
- `average_precision_score`: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html

### Visualisierung
- matplotlib `pyplot`: https://matplotlib.org/stable/api/pyplot_summary.html

### SHAP (Feature-Erklärbarkeit)
- SHAP-Dokumentation: https://shap.readthedocs.io/en/latest/
- `TreeExplainer`: https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html
