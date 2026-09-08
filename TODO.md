# TODO / Laufende Aufgaben (Bachelorarbeit)

> Lokale Notizdatei (gitignored). Stand: 2026-09-08 – Deadline Entwicklung: ~16 Tage.

## Erledigt ✅
- [x] **P12** Lauf abgeschlossen (85 KPIs)
- [x] **P13** Lauf abgeschlossen (100 KPIs, synthetische Fixtures)
- [x] KPI-CSV neu gezogen: `export_kpis/all_projects_kpis_new.csv` (675 Zeilen)

## Ablauf jetzt – Schritt für Schritt
### 1) P06 komplett laufen lassen (Fix-Stand prüfen)
- [ ] test/P06 prüfen (Fix d08f7a9 committet, tests.json = 6 Tests?)
- [ ] Push auf test/P06 (Push-Trigger aktiv) → kompletter Lauf (nur pos_046 bisher im Bucket)
- [ ] KPIs prüfen (6 × 5 = 30 erwartet)
- erledigt ! 

### 2) P07 fixen (6 Methoden: pos_053/054/056/057/059/061 = 100 % Fehler)
- [ ] Ursache finden (Locust-Ziel/App/Seed)
- [ ] Fix + lokaler Smoke (0 % Fehler)
- [ ] Neulauf der 6 Methoden

### 3) P03 lauffähig machen (BLEIBT im Dataset) – SMTP-Sink-Fix
- [ ] SMTP-Sink (aiosmtpd) lokal im P03-App-Container starten (damit `/api/mail` Erfolg liefert)
- [ ] P03-Positiv neu laufen (pos_027/028, 2×5 = 10 KPIs)
- [ ] P03 gehört in den Negativ-Kern (2 Negativ-Läufe: pos_027/028)

### 4) Entscheidung P01 / P05 / P08 (optional Neulauf – nur wenn Zeit)
- [ ] P01 (Legacy-Infra), P05 (verrauscht), P08 (high/extreme-Fehler)

### 5) Negativ-Kampagne (max. 32 Läufe, Kern-Projekte)
- [ ] Kern: P02, P03, P04, P06, P09, P10, P11 (Verteilung der 32 Läufe liegt beim Autor)
- [ ] Pro Lauf: 1 Negativ-Mutation → gleicher Test → KPI (Infra im Projekt halten)
- [ ] Neg-KPI-Präfix (z. B. `P02_neg`) + Helfer dokumentieren

### 6) ML / Auswertung
- [ ] Trainings-Notebook (Pos/Neg: LogReg → LightGBM), Split nach Projekt
- [ ] F1/PR-AUC, Confusion, SHAP
- [ ] Evaluation P12/P13 (held-out)

### 7) Technische Nachzügler
- [ ] Image-Tag-Fix P08 (und P01/P06 nach Läufen)
- [ ] `run_ecs_task.py`-Rollout (db_seed + asyncio)
- [ ] Handbuch pflegen

### 8) Verschriftlichung (parallel zu Läufen!)
- [ ] Kapitel schreiben, während Läufe laufen
