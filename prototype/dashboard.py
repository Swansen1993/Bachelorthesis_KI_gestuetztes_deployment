import json
import pathlib

import altair as alt
import pandas as pd
import streamlit as st

MODULORDNER = pathlib.Path(__file__).resolve().parent
FARBE_INSTABIL = "#c0392b"
FARBE_STABIL = "#2e7d32"
FARBE_START = "#7f8c8d"
FARBE_SUMME = "#2c3e50"

st.set_page_config(page_title="Stabilitätsbewertung der Pipeline", layout="wide")


def lade_protokoll(pfad):
    with open(pfad, encoding="utf-8") as datei:
        return [json.loads(zeile) for zeile in datei if zeile.strip()]


def ist_protokoll(pfad):
    try:
        with open(pfad, encoding="utf-8") as datei:
            erste = datei.readline()
    except OSError:
        return False
    if not erste.strip():
        return False
    try:
        zeile = json.loads(erste)
    except json.JSONDecodeError:
        return False
    return isinstance(zeile, dict) and "modellvorhersage" in zeile


def protokollkandidaten():
    return sorted(pfad for pfad in MODULORDNER.glob("*.jsonl") if ist_protokoll(pfad))


def uebersichtstabelle(zeilen):
    return pd.DataFrame(
        [
            {
                "Fall": f"{zeile['projekt']}/{zeile['nummer']}",
                "Methode": zeile["methode"],
                "Umgebung": zeile["umgebung"],
                "Code": "unverändert" if zeile.get("kontrolle") else "verändert",
                "Punktwert": zeile["erklaerung"]["punktwert"],
                "Einstufung": zeile["erklaerung"]["einstufung"],
                "Wahrscheinlichkeit instabil in Prozent": zeile["modellvorhersage"][
                    "wahrscheinlichkeit_mutiert_prozent"
                ],
                "Modellurteil": zeile["modellvorhersage"]["urteil"],
                "Anzeige": zeile["anzeige"]["anzeige"],
                "Agentenklasse": str(
                    (zeile.get("antwort") or {}).get("fehlerklasse", "")
                ),
                "Erwartete Klasse": str(zeile.get("erwartete_klasse", "")),
            }
            for zeile in zeilen
        ]
    )


def fallschluessel(zeile):
    return (
        zeile.get("projekt"),
        zeile.get("nummer"),
        zeile.get("methode"),
        zeile.get("umgebung"),
        zeile.get("kontrolle"),
    )


def fallbeschriftungen(zeilen):
    anzahl = {}
    for zeile in zeilen:
        schluessel = fallschluessel(zeile)
        anzahl[schluessel] = anzahl.get(schluessel, 0) + 1
    beschriftungen = []
    for zeile in zeilen:
        text = (
            f"{zeile['projekt']}/{zeile['nummer']} · {zeile['methode']} · "
            f"{zeile['umgebung']} · "
            f"{'unverändert' if zeile.get('kontrolle') else 'verändert'}"
        )
        if anzahl[fallschluessel(zeile)] > 1:
            text += f" · Runde {zeile.get('runde', 1)}"
        beschriftungen.append(text)
    return beschriftungen


def gegenueberstellung(zeilen):
    paare = {}
    for zeile in zeilen:
        schluessel = (
            zeile["projekt"],
            zeile["nummer"],
            zeile["methode"],
            zeile["umgebung"],
        )
        seite = "unverändert" if zeile.get("kontrolle") else "verändert"
        paare.setdefault(schluessel, {})[seite] = zeile
    eintraege = []
    for (projekt, nummer, methode, umgebung), seiten in paare.items():
        if len(seiten) < 2:
            continue
        veraendert = seiten["verändert"]
        unveraendert = seiten["unverändert"]
        eintraege.append(
            {
                "Fall": f"{projekt}/{nummer}",
                "Methode": methode,
                "Umgebung": umgebung,
                "Punkte verändert": veraendert["erklaerung"]["punktwert"],
                "Punkte unverändert": unveraendert["erklaerung"]["punktwert"],
                "Instabil verändert": veraendert["modellvorhersage"][
                    "wahrscheinlichkeit_mutiert_prozent"
                ],
                "Instabil unverändert": unveraendert["modellvorhersage"][
                    "wahrscheinlichkeit_mutiert_prozent"
                ],
                "Urteil verändert": veraendert["modellvorhersage"]["urteil"],
                "Urteil unverändert": unveraendert["modellvorhersage"]["urteil"],
                "Fehlalarm": bool(
                    unveraendert["modellvorhersage"]["urteil"] == "instabil"
                ),
            }
        )
    return pd.DataFrame(eintraege)


def kriterientabelle(zeilen):
    return pd.DataFrame(
        [
            {
                "Kriterium": k["kriterium"],
                "Abweichung in Prozent": k["abweichung_prozent"],
                "Gewicht": k["gewicht"],
                "Punkte": k["punkte"],
                "Beitrag zum Punktwert": k["beitrag_zum_punktwert"],
            }
            for k in zeilen
        ]
    )


def stufentabelle(zeilen):
    return pd.DataFrame(
        [
            {
                "Umgebungsstufe": e["umgebungsstufe"],
                "Punktwert": e["punktwert"],
                "Einstufung": e["einstufung"],
                "Hauptursache": e["hauptursache"],
            }
            for e in zeilen
        ]
    )


def zerlegungsdaten(block):
    schritte = [
        {
            "Schritt": "Ausgangswert",
            "von": 0.0,
            "bis": block["ausgangswert"],
            "Art": "Ausgangswert",
        }
    ]
    lauf = block["ausgangswert"]
    for eintrag in block["beitraege"]:
        neu = lauf + eintrag["beitrag"]
        schritte.append(
            {
                "Schritt": eintrag["merkmal"],
                "von": lauf,
                "bis": neu,
                "Art": eintrag["spricht_fuer"],
            }
        )
        lauf = neu
    schritte.append({"Schritt": "Summe", "von": 0.0, "bis": lauf, "Art": "Summe"})
    return pd.DataFrame(schritte)


def zerlegungsbild(block):
    daten = zerlegungsdaten(block)
    return (
        alt.Chart(daten)
        .mark_bar()
        .encode(
            x=alt.X("von", title="Modelleinheiten"),
            x2="bis",
            y=alt.Y("Schritt", sort=None, title=None),
            color=alt.Color(
                "Art",
                scale=alt.Scale(
                    domain=["instabil", "nicht instabil", "Ausgangswert", "Summe"],
                    range=[FARBE_INSTABIL, FARBE_STABIL, FARBE_START, FARBE_SUMME],
                ),
                legend=None,
            ),
            tooltip=["Schritt", "von", "bis", "Art"],
        )
        .properties(height=200)
    )


def kopfzeile(zeile):
    st.markdown(f"### {zeile['projekt']}/{zeile['nummer']} · {zeile['methode']}")
    st.caption(
        f"Code {'unverändert' if zeile.get('kontrolle') else 'verändert'} · "
        f"Datei {zeile.get('datei') or 'unbekannt'} · "
        f"Umgebungsstufe {zeile['umgebung']} · "
        f"Ansicht {zeile.get('ansicht')} · Runde {zeile.get('runde')} · "
        f"Modell {zeile.get('modell')}"
    )


def scoreblock(zeile):
    erklaerung = zeile["erklaerung"]
    st.subheader("Score aus der KPI-Matrix")
    spalten = st.columns(3)
    spalten[0].metric("Punktwert", erklaerung["punktwert"])
    spalten[1].metric("Einstufung", erklaerung["einstufung"])
    spalten[2].metric(
        "Hauptursache", erklaerung.get("hauptursache", "nicht überliefert")
    )
    st.caption(erklaerung["formel"])
    st.dataframe(kriterientabelle(erklaerung["kriterien"]), hide_index=True)
    for hinweis in erklaerung["hinweise"] or []:
        st.info(hinweis)
    with st.expander("Alle Umgebungsstufen"):
        st.dataframe(stufentabelle(erklaerung["umgebungen"]), hide_index=True)


def modellblock(zeile):
    block = zeile["modellvorhersage"]
    st.subheader("Modell und seine Erklärung")
    spalten = st.columns(3)
    spalten[0].metric(
        "Wahrscheinlichkeit instabil",
        f"{block['wahrscheinlichkeit_mutiert_prozent']} %",
    )
    spalten[1].metric("Urteil des Modells", block["urteil"])
    spalten[2].metric(
        "Entscheidungsgrenze", f"{block['entscheidungsgrenze_prozent']} %"
    )
    st.altair_chart(zerlegungsbild(block))
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Beitrag": eintrag["merkmal"],
                    "Wert": eintrag["beitrag"],
                    "Spricht für": eintrag["spricht_fuer"],
                }
                for eintrag in block["beitraege"]
            ]
        ),
        hide_index=True,
    )
    summe = round(
        block["ausgangswert"] + sum(e["beitrag"] for e in block["beitraege"]), 3
    )
    st.caption(
        f"Ausgangswert {block['ausgangswert']} + Beiträge = {summe} "
        f"(Modellwert {block['summe']}). Die Zerlegung ist genau: {block['summe_stimmt']}."
    )
    st.caption(
        "Die Beiträge stehen in Modelleinheiten, nicht in Prozent. Ein positiver Beitrag "
        "kann auch bei einer von Natur aus langsamen Methode auftreten, ohne dass eine "
        "Mutation vorliegt."
    )


def agentenblock(zeile):
    st.subheader("Antwort des Agenten")
    anzeige = zeile["anzeige"]
    st.markdown(f"**{anzeige['anzeige']}**")
    if anzeige.get("qualifizierter_hinweis"):
        st.warning(anzeige["qualifizierter_hinweis"])
    st.markdown(zeile.get("begruendung") or "_keine Prosa überliefert_")
    antwort = zeile.get("antwort") or {}
    spalten = st.columns(3)
    spalten[0].metric("Fehlerklasse", str(antwort.get("fehlerklasse", "")))
    stelle = antwort.get("codestelle") or {}
    spalten[1].metric("Genannte Zeile", str(stelle.get("zeile", "")))
    spalten[2].metric("Erwartete Klasse", str(zeile.get("erwartete_klasse", "")))
    if antwort.get("empfehlung"):
        st.info(antwort["empfehlung"])
    pruefung = zeile.get("pruefung") or {}
    st.caption(
        f"Geänderte Zeilen: {zeile.get('geaenderte_zeilen')} · "
        f"Kernzeilen: {pruefung.get('kernzeilen')} · "
        f"Abstand: {pruefung.get('abstand')} · "
        f"Zitat exakt: {pruefung.get('exakt_zitat')}"
    )
    with st.expander("Ausschnitt, den der Agent gesehen hat"):
        st.code(zeile.get("ausschnitt") or "", language="python")
    with st.expander("Gemessene Werte"):
        st.json(zeile.get("messwerte") or {})


st.title("Stabilitätsbewertung der Pipeline")

kandidaten = protokollkandidaten()
vorgabe = str(kandidaten[-1]) if kandidaten else ""
eingabe = st.sidebar.text_input("Protokolldatei", value=vorgabe)
if kandidaten:
    st.sidebar.caption(
        "Gefundene Protokolle:\n\n" + "\n\n".join(p.name for p in kandidaten)
    )

if not eingabe:
    st.info(
        "Keine Protokolldatei angegeben. Sie entsteht mit "
        "`python prototype/harness.py --lauf --umgebung <stufe> --antwortdatei <datei>`."
    )
    st.stop()

pfad = pathlib.Path(eingabe)
if not pfad.exists():
    st.error(f"Datei nicht gefunden: {pfad}")
    st.stop()

zeilen = lade_protokoll(pfad)
if not zeilen:
    st.warning("Die Datei enthält keine Zeilen.")
    st.stop()

st.sidebar.caption(f"{len(zeilen)} Zeilen in {pfad.name}")

uebersicht, einzelner = st.tabs(["Übersicht", "Einzelfall"])

with uebersicht:
    tabelle = uebersichtstabelle(zeilen)
    spalten = st.columns(4)
    spalten[0].metric("Fälle im Protokoll", len(tabelle))
    spalten[1].metric("Matrix auffällig", int((tabelle["Punktwert"] < 75).sum()))
    spalten[2].metric(
        "Modell sagt instabil", int((tabelle["Modellurteil"] == "instabil").sum())
    )
    spalten[3].metric(
        "Beide auffällig",
        int(
            (
                (tabelle["Punktwert"] < 75) & (tabelle["Modellurteil"] == "instabil")
            ).sum()
        ),
    )
    st.dataframe(tabelle, hide_index=True)
    paare = gegenueberstellung(zeilen)
    if not paare.empty:
        st.subheader("Gegenüberstellung: veränderter gegen unveränderten Code")
        st.dataframe(paare, hide_index=True)
        st.caption(
            "Beide Zeilen stammen aus demselben Lauf. Bei den unveränderten Zeilen "
            "steht der Punktwert im Kampagnenaufbau immer auf 100, weil die gesunde "
            "Messung ihre eigene Referenz ist; aussagekräftig ist dort die Spalte "
            "Fehlalarm."
        )
    st.caption(
        "Punktwert und Modellwert sind nicht austauschbar: Der Punktwert folgt den Bändern "
        "der Matrix, der Modellwert der Vorhersage aus den Messwerten. Beide stehen "
        "nebeneinander und werden nicht verrechnet. Die Prozentangabe ist die "
        "Modellausgabe zur Frage, ob der Code verändert wurde; lesbar wird sie "
        "erst mit der Entscheidungsgrenze von 2,7 Prozent. Sie sagt nichts über "
        "die Schwere der Änderung."
    )

with einzelner:
    beschriftungen = fallbeschriftungen(zeilen)
    auswahl = st.selectbox(
        "Fall", range(len(zeilen)), format_func=lambda i: beschriftungen[i]
    )
    zeile = zeilen[auswahl]
    kopfzeile(zeile)
    links, rechts = st.columns(2)
    with links:
        scoreblock(zeile)
    with rechts:
        modellblock(zeile)
    st.divider()
    agentenblock(zeile)
