"""
Dokumentenanforderung - Anwaltsseite

Ermoeglicht Anwaelten, spezifische Dokumente von Mandanten anzufordern.
Die Anforderungen erscheinen prominent auf dem Mandanten-Dashboard.
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from enum import Enum


class DokumentKategorie(Enum):
    """Kategorien fuer angeforderte Dokumente"""
    PERSOENLICHE_DOKUMENTE = "Persoenliche Dokumente"
    EINKOMMENSNACHWEISE = "Einkommensnachweise"
    VERMOEGEN_IMMOBILIEN = "Vermoegen & Immobilien"
    FAMILIENRECHT = "Familienrechtliche Dokumente"
    KINDER = "Dokumente zu Kindern"
    SCHULDEN_VERBINDLICHKEITEN = "Schulden & Verbindlichkeiten"
    VERSICHERUNGEN = "Versicherungen & Vorsorge"
    SONSTIGES = "Sonstige Dokumente"


# Vordefinierte Dokumenttypen nach Kategorie
DOKUMENT_TYPEN: Dict[DokumentKategorie, List[Dict]] = {
    DokumentKategorie.PERSOENLICHE_DOKUMENTE: [
        {"id": "personalausweis", "name": "Personalausweis / Reisepass", "beschreibung": "Kopie des gueltigen Ausweisdokuments"},
        {"id": "meldebescheinigung", "name": "Meldebescheinigung", "beschreibung": "Aktuelle Meldebescheinigung vom Einwohnermeldeamt"},
        {"id": "lebenslauf", "name": "Lebenslauf", "beschreibung": "Tabellarischer Lebenslauf"},
    ],
    DokumentKategorie.EINKOMMENSNACHWEISE: [
        {"id": "gehaltsabrechnung_3m", "name": "Gehaltsabrechnungen (letzte 3 Monate)", "beschreibung": "Die letzten drei Gehaltsabrechnungen"},
        {"id": "gehaltsabrechnung_12m", "name": "Gehaltsabrechnungen (letzte 12 Monate)", "beschreibung": "Alle Gehaltsabrechnungen der letzten 12 Monate"},
        {"id": "steuerbescheid", "name": "Steuerbescheid", "beschreibung": "Letzter Einkommensteuerbescheid"},
        {"id": "steuererklaerung", "name": "Steuererklaerung", "beschreibung": "Letzte Einkommensteuererklaerung mit Anlagen"},
        {"id": "arbeitsvertrag", "name": "Arbeitsvertrag", "beschreibung": "Aktueller Arbeitsvertrag"},
        {"id": "kuendigungsschreiben", "name": "Kuendigungsschreiben", "beschreibung": "Kuendigung des Arbeitsverhaeltnisses"},
        {"id": "arbeitslosengeld", "name": "ALG I/II Bescheid", "beschreibung": "Aktueller Bescheid ueber Arbeitslosengeld"},
        {"id": "rentenbescheid", "name": "Rentenbescheid", "beschreibung": "Aktueller Rentenbescheid"},
        {"id": "elterngeld", "name": "Elterngeldbescheid", "beschreibung": "Bescheid ueber Elterngeld"},
        {"id": "selbstaendig_bilanz", "name": "Bilanz / GuV (Selbstaendige)", "beschreibung": "Bilanz und Gewinn- und Verlustrechnung der letzten 3 Jahre"},
        {"id": "selbstaendig_bwa", "name": "BWA (Selbstaendige)", "beschreibung": "Aktuelle Betriebswirtschaftliche Auswertung"},
    ],
    DokumentKategorie.VERMOEGEN_IMMOBILIEN: [
        {"id": "grundbuchauszug", "name": "Grundbuchauszug", "beschreibung": "Aktueller Grundbuchauszug aller Immobilien"},
        {"id": "kaufvertrag_immobilie", "name": "Kaufvertrag Immobilie", "beschreibung": "Notarieller Kaufvertrag der Immobilie"},
        {"id": "wertgutachten", "name": "Wertgutachten Immobilie", "beschreibung": "Aktuelles Wertgutachten / Verkehrswertgutachten"},
        {"id": "mietvertrag", "name": "Mietvertrag", "beschreibung": "Aktueller Mietvertrag"},
        {"id": "nebenkostenabrechnung", "name": "Nebenkostenabrechnung", "beschreibung": "Letzte Nebenkostenabrechnung"},
        {"id": "kontoauszuege", "name": "Kontoauszuege", "beschreibung": "Kontoauszuege aller Konten der letzten 3-12 Monate"},
        {"id": "depotauszug", "name": "Depotauszug", "beschreibung": "Aktueller Depotauszug / Wertpapieraufstellung"},
        {"id": "kfz_brief", "name": "Fahrzeugbrief / Zulassung", "beschreibung": "Fahrzeugbrief und Zulassungsbescheinigung"},
        {"id": "handelsregister", "name": "Handelsregisterauszug", "beschreibung": "Aktueller Handelsregisterauszug"},
        {"id": "gesellschaftsvertrag", "name": "Gesellschaftsvertrag", "beschreibung": "Gesellschaftsvertrag / Satzung"},
    ],
    DokumentKategorie.FAMILIENRECHT: [
        {"id": "heiratsurkunde", "name": "Heiratsurkunde", "beschreibung": "Heiratsurkunde / Eheurkunde"},
        {"id": "ehevertrag", "name": "Ehevertrag", "beschreibung": "Notarieller Ehevertrag (falls vorhanden)"},
        {"id": "trennungsvereinbarung", "name": "Trennungsvereinbarung", "beschreibung": "Schriftliche Trennungsvereinbarung"},
        {"id": "scheidungsurteil", "name": "Scheidungsurteil", "beschreibung": "Frueheres Scheidungsurteil (bei Wiederheirat)"},
        {"id": "versorgungsausgleich", "name": "Versorgungsausgleich", "beschreibung": "Beschluss zum Versorgungsausgleich"},
        {"id": "unterhaltstitel", "name": "Unterhaltstitel", "beschreibung": "Bestehende Unterhaltstitel / Urkunden"},
        {"id": "sorgerechtsbeschluss", "name": "Sorgerechtsbeschluss", "beschreibung": "Gerichtlicher Beschluss zum Sorgerecht"},
        {"id": "umgangsregelung", "name": "Umgangsregelung", "beschreibung": "Vereinbarung oder Beschluss zum Umgangsrecht"},
    ],
    DokumentKategorie.KINDER: [
        {"id": "geburtsurkunde_kind", "name": "Geburtsurkunde Kind", "beschreibung": "Geburtsurkunde des Kindes / der Kinder"},
        {"id": "vaterschaftsanerkennung", "name": "Vaterschaftsanerkennung", "beschreibung": "Urkunde ueber Vaterschaftsanerkennung"},
        {"id": "kindergeldbescheid", "name": "Kindergeldbescheid", "beschreibung": "Aktueller Kindergeldbescheid"},
        {"id": "schulbescheinigung", "name": "Schulbescheinigung", "beschreibung": "Aktuelle Schulbescheinigung"},
        {"id": "ausbildungsvertrag", "name": "Ausbildungsvertrag", "beschreibung": "Ausbildungsvertrag des Kindes"},
        {"id": "studienbescheinigung", "name": "Studienbescheinigung", "beschreibung": "Immatrikulationsbescheinigung"},
        {"id": "bafoeg_bescheid", "name": "BAFoeG-Bescheid", "beschreibung": "BAFoeG-Bescheid des Kindes"},
        {"id": "kinderbetreuung", "name": "Kinderbetreuungskosten", "beschreibung": "Nachweise ueber Kinderbetreuungskosten"},
    ],
    DokumentKategorie.SCHULDEN_VERBINDLICHKEITEN: [
        {"id": "kreditvertrag", "name": "Kreditvertrag", "beschreibung": "Kreditvertraege und Darlehensvertraege"},
        {"id": "tilgungsplan", "name": "Tilgungsplan", "beschreibung": "Aktueller Tilgungsplan"},
        {"id": "schuldenuebersicht", "name": "Schuldenuebersicht", "beschreibung": "Aufstellung aller Schulden und Verbindlichkeiten"},
        {"id": "insolvenzunterlagen", "name": "Insolvenzunterlagen", "beschreibung": "Unterlagen zur Privatinsolvenz"},
        {"id": "unterhaltszahlungen", "name": "Nachweise Unterhaltszahlungen", "beschreibung": "Nachweise ueber geleistete Unterhaltszahlungen"},
    ],
    DokumentKategorie.VERSICHERUNGEN: [
        {"id": "rentenauskunft", "name": "Rentenauskunft", "beschreibung": "Aktuelle Rentenauskunft der DRV"},
        {"id": "lebensversicherung", "name": "Lebensversicherung", "beschreibung": "Police und Wertmitteilung Lebensversicherung"},
        {"id": "betriebsrente", "name": "Betriebsrentenauskunft", "beschreibung": "Auskunft zur betrieblichen Altersvorsorge"},
        {"id": "riester_ruerup", "name": "Riester/Ruerup-Vertrag", "beschreibung": "Unterlagen zu Riester- oder Ruerup-Rente"},
        {"id": "private_krankenversicherung", "name": "Private Krankenversicherung", "beschreibung": "PKV-Vertrag und Beitragsnachweis"},
        {"id": "berufsunfaehigkeit", "name": "Berufsunfaehigkeitsversicherung", "beschreibung": "BU-Versicherung Police"},
    ],
    DokumentKategorie.SONSTIGES: [
        {"id": "vollmacht", "name": "Vollmacht", "beschreibung": "Unterschriebene Vollmacht"},
        {"id": "schriftverkehr_gegner", "name": "Schriftverkehr mit Gegenseite", "beschreibung": "Bisheriger Schriftverkehr mit der Gegenseite"},
        {"id": "schriftverkehr_gericht", "name": "Schriftverkehr mit Gericht", "beschreibung": "Bisheriger Schriftverkehr mit dem Gericht"},
        {"id": "sonstiges", "name": "Sonstige Dokumente", "beschreibung": "Weitere relevante Dokumente"},
    ],
}


def render_dokumentenanforderung_page():
    """Hauptseite fuer Dokumentenanforderungen"""
    st.header("Dokumentenanforderung")

    # Tabs fuer verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs([
        "Neue Anforderung",
        "Offene Anforderungen",
        "Erledigte Anforderungen"
    ])

    with tab1:
        render_neue_anforderung()

    with tab2:
        render_offene_anforderungen()

    with tab3:
        render_erledigte_anforderungen()


def render_neue_anforderung():
    """Formular fuer neue Dokumentenanforderung"""
    st.subheader("Dokumente vom Mandanten anfordern")

    # Akte auswaehlen (Demo-Daten)
    akten = [
        {"id": "1", "az": "2026/0001", "mandant": "Max Mustermann", "typ": "Scheidung"},
        {"id": "2", "az": "2026/0015", "mandant": "Lisa Schmidt", "typ": "Kindesunterhalt"},
        {"id": "3", "az": "2026/0008", "mandant": "Peter Meyer", "typ": "Trennungsunterhalt"},
    ]

    akte_optionen = [f"{a['az']} - {a['mandant']} ({a['typ']})" for a in akten]
    ausgewaehlte_akte = st.selectbox("Akte auswaehlen", akte_optionen)

    st.markdown("---")

    # Schnellauswahl nach Falltyp
    st.markdown("#### Schnellauswahl nach Verfahrensart")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Scheidung (Standard)", use_container_width=True):
            st.session_state.schnellauswahl = [
                "heiratsurkunde", "geburtsurkunde_kind", "gehaltsabrechnung_12m",
                "steuerbescheid", "kontoauszuege", "grundbuchauszug",
                "rentenauskunft", "lebensversicherung"
            ]

    with col2:
        if st.button("Kindesunterhalt", use_container_width=True):
            st.session_state.schnellauswahl = [
                "geburtsurkunde_kind", "gehaltsabrechnung_3m", "steuerbescheid",
                "kindergeldbescheid", "schulbescheinigung"
            ]

    with col3:
        if st.button("Zugewinnausgleich", use_container_width=True):
            st.session_state.schnellauswahl = [
                "heiratsurkunde", "grundbuchauszug", "kontoauszuege",
                "depotauszug", "lebensversicherung", "kfz_brief",
                "steuerbescheid", "wertgutachten"
            ]

    st.markdown("---")

    # Dokumentauswahl nach Kategorien
    st.markdown("#### Dokumente auswaehlen")

    ausgewaehlte_dokumente = []
    schnellauswahl = st.session_state.get("schnellauswahl", [])

    for kategorie in DokumentKategorie:
        with st.expander(f"{kategorie.value}", expanded=False):
            dokumente = DOKUMENT_TYPEN.get(kategorie, [])

            for dok in dokumente:
                # Pruefen ob in Schnellauswahl
                default_checked = dok["id"] in schnellauswahl

                col1, col2 = st.columns([3, 2])
                with col1:
                    if st.checkbox(
                        dok["name"],
                        value=default_checked,
                        key=f"dok_{dok['id']}",
                        help=dok["beschreibung"]
                    ):
                        ausgewaehlte_dokumente.append(dok)
                with col2:
                    st.caption(dok["beschreibung"])

    st.markdown("---")

    # Zusaetzliche Optionen
    st.markdown("#### Anforderungsdetails")

    col1, col2 = st.columns(2)

    with col1:
        prioritaet = st.selectbox(
            "Prioritaet",
            ["Normal", "Hoch", "Dringend"],
            help="Bei 'Dringend' erhaelt der Mandant eine Benachrichtigung"
        )

        frist = st.date_input(
            "Frist",
            value=date.today() + timedelta(days=14),
            min_value=date.today(),
            help="Bis wann sollen die Dokumente eingereicht werden?"
        )

    with col2:
        erinnerung = st.checkbox(
            "Automatische Erinnerung senden",
            value=True,
            help="Mandant erhaelt Erinnerung 3 Tage vor Fristablauf"
        )

        benachrichtigung = st.selectbox(
            "Benachrichtigung",
            ["Im System", "Im System + E-Mail"],
            help="Wie soll der Mandant benachrichtigt werden?"
        )

    # Individuelle Nachricht
    nachricht = st.text_area(
        "Nachricht an den Mandanten (optional)",
        placeholder="Sehr geehrte(r) Mandant(in),\n\nbitte reichen Sie die oben genannten Unterlagen ein...",
        height=100
    )

    st.markdown("---")

    # Zusammenfassung und Absenden
    if ausgewaehlte_dokumente:
        st.markdown("#### Zusammenfassung")
        st.info(f"**{len(ausgewaehlte_dokumente)} Dokumente** werden angefordert")

        with st.expander("Ausgewaehlte Dokumente anzeigen"):
            for dok in ausgewaehlte_dokumente:
                st.write(f"- {dok['name']}")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("Anforderung senden", type="primary", use_container_width=True):
                st.success(f"Anforderung fuer {len(ausgewaehlte_dokumente)} Dokumente wurde an den Mandanten gesendet!")
                st.session_state.schnellauswahl = []
                st.balloons()

        with col2:
            if st.button("Zuruecksetzen", use_container_width=True):
                st.session_state.schnellauswahl = []
                st.rerun()
    else:
        st.warning("Bitte waehlen Sie mindestens ein Dokument aus.")


def render_offene_anforderungen():
    """Zeigt offene Dokumentenanforderungen"""
    st.subheader("Offene Anforderungen")

    # Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_akte = st.selectbox("Nach Akte filtern", ["Alle Akten", "2026/0001", "2026/0015", "2026/0008"])
    with col2:
        filter_prioritaet = st.selectbox("Nach Prioritaet filtern", ["Alle", "Dringend", "Hoch", "Normal"])
    with col3:
        filter_frist = st.selectbox("Nach Frist filtern", ["Alle", "Ueberfaellig", "Diese Woche", "Dieser Monat"])

    st.markdown("---")

    # Demo-Daten fuer offene Anforderungen
    offene_anforderungen = [
        {
            "id": "1",
            "akte": "2026/0001",
            "mandant": "Max Mustermann",
            "dokumente": ["Gehaltsabrechnungen (letzte 12 Monate)", "Steuerbescheid", "Grundbuchauszug"],
            "erstellt": "10.01.2026",
            "frist": "24.01.2026",
            "prioritaet": "Hoch",
            "status": "Teilweise eingereicht",
            "eingereicht": 1,
            "gesamt": 3
        },
        {
            "id": "2",
            "akte": "2026/0015",
            "mandant": "Lisa Schmidt",
            "dokumente": ["Geburtsurkunde Kind", "Kindergeldbescheid"],
            "erstellt": "08.01.2026",
            "frist": "15.01.2026",
            "prioritaet": "Dringend",
            "status": "Offen",
            "eingereicht": 0,
            "gesamt": 2
        },
        {
            "id": "3",
            "akte": "2026/0008",
            "mandant": "Peter Meyer",
            "dokumente": ["Arbeitsvertrag", "Kontoauszuege", "Mietvertrag", "Rentenauskunft"],
            "erstellt": "05.01.2026",
            "frist": "31.01.2026",
            "prioritaet": "Normal",
            "status": "Offen",
            "eingereicht": 0,
            "gesamt": 4
        },
    ]

    for anf in offene_anforderungen:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                st.markdown(f"**{anf['akte']} - {anf['mandant']}**")
                st.caption(f"{anf['gesamt']} Dokumente angefordert")

            with col2:
                if anf['prioritaet'] == "Dringend":
                    st.error(f"Prioritaet: {anf['prioritaet']}")
                elif anf['prioritaet'] == "Hoch":
                    st.warning(f"Prioritaet: {anf['prioritaet']}")
                else:
                    st.info(f"Prioritaet: {anf['prioritaet']}")

            with col3:
                st.write(f"Frist: {anf['frist']}")
                # Fortschrittsbalken
                progress = anf['eingereicht'] / anf['gesamt']
                st.progress(progress, text=f"{anf['eingereicht']}/{anf['gesamt']} eingereicht")

            with col4:
                if st.button("Details", key=f"detail_{anf['id']}", use_container_width=True):
                    st.session_state.selected_anforderung = anf['id']

                if st.button("Erinnerung", key=f"remind_{anf['id']}", use_container_width=True):
                    st.success(f"Erinnerung an {anf['mandant']} gesendet!")

            with st.expander("Angeforderte Dokumente"):
                for dok in anf['dokumente']:
                    st.write(f"- {dok}")

            st.markdown("---")


def render_erledigte_anforderungen():
    """Zeigt erledigte Dokumentenanforderungen"""
    st.subheader("Erledigte Anforderungen")

    # Demo-Daten
    erledigte = [
        {
            "akte": "2025/0089",
            "mandant": "Klaus Wagner",
            "dokumente": 5,
            "abgeschlossen": "03.01.2026"
        },
        {
            "akte": "2025/0156",
            "mandant": "Maria Bauer",
            "dokumente": 8,
            "abgeschlossen": "28.12.2025"
        },
    ]

    for anf in erledigte:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{anf['akte']} - {anf['mandant']}**")
        with col2:
            st.write(f"{anf['dokumente']} Dokumente")
        with col3:
            st.success(f"Erledigt: {anf['abgeschlossen']}")
        st.markdown("---")


def render_dokument_kategorien_verwaltung():
    """Verwaltung der Dokumentkategorien (Admin-Funktion)"""
    st.subheader("Dokumentkategorien verwalten")

    st.info("Hier koennen Administratoren neue Dokumenttypen hinzufuegen oder bestehende bearbeiten.")

    # Kategorie auswaehlen
    kategorie = st.selectbox(
        "Kategorie",
        [k.value for k in DokumentKategorie]
    )

    # Bestehende Dokumenttypen anzeigen
    st.markdown("#### Bestehende Dokumenttypen")

    for kat in DokumentKategorie:
        if kat.value == kategorie:
            dokumente = DOKUMENT_TYPEN.get(kat, [])
            for dok in dokumente:
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(dok["name"])
                with col2:
                    st.caption(dok["beschreibung"])
                with col3:
                    st.button("Bearbeiten", key=f"edit_{dok['id']}", disabled=True)

    # Neuen Dokumenttyp hinzufuegen
    st.markdown("---")
    st.markdown("#### Neuen Dokumenttyp hinzufuegen")

    col1, col2 = st.columns(2)
    with col1:
        neuer_name = st.text_input("Name")
    with col2:
        neue_beschreibung = st.text_input("Beschreibung")

    if st.button("Hinzufuegen", disabled=True):
        st.info("Diese Funktion ist in der Demo deaktiviert.")
