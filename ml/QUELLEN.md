# Quellenverzeichnis

Gilt für Code/Doku in diesem Projekt (wichtigste Regel: Quellen angeben, präzise benennen, verlinken, prüfen). Diese Liste wird laufend ergänzt und gehört später inhaltlich ins PROJEKTHANDBUCH.

## ML / Klassifikation (Notebook: ml/posneg_klassifikator.ipynb)

| Code-Anteil | Quelle (präzise) | Link |
|---|---|---|
| CSV laden | pandas Dokumentation – `pandas.read_csv` | https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html |
| Datenaufbereitung/DataFrame | pandas Dokumentation – User Guide | https://pandas.pydata.org/docs/user_guide/index.html |
| Projekt-Split (keine Leakage) | scikit-learn – `sklearn.model_selection.GroupShuffleSplit` | https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html |
| Train/Test-Grundlagen | scikit-learn – `train_test_split` + Modellauswahl | https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html |
| Fehlende Werte | scikit-learn – `sklearn.impute.SimpleImputer` | https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html |
| Skalierung | scikit-learn – `sklearn.preprocessing.StandardScaler` | https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html |
| Preprocessing-Pipeline | scikit-learn – `sklearn.pipeline.Pipeline` | https://scikit-learn.org/stable/modules/compose.html |
| Baseline-Modell | scikit-learn – `sklearn.linear_model.LogisticRegression` | https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html |
| Ensemble-Modell | scikit-learn – `sklearn.ensemble.RandomForestClassifier` | https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html |
| Gradient Boosting | LightGBM – `lightgbm.LGBMClassifier` (Python API) | https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.LGBMClassifier.html |
| Metriken | scikit-learn – Model Evaluation (f1_score, confusion_matrix, precision_recall_curve, average_precision_score) | https://scikit-learn.org/stable/modules/model_evaluation.html |
| Erklärbarkeit | SHAP – `shap.TreeExplainer` + Summary Plot | https://shap.readthedocs.io/en/latest/ und https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html |
| Visualisierung | Matplotlib – Pyplot-Tutorial | https://matplotlib.org/stable/tutorials/pyplot.html |

## Hinweise
- Quellen werden vor Verwendung doppelt/dreifach gegen den erzeugten Code geprüft (Versionen, API-Namen, Syntax).
- Diese Liste ist die Referenz für die Abschnitte „Quellen/Eingesetzte Werkzeuge" im PROJEKTHANDBUCH und die Verschriftlichung.
