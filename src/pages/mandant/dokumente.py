"""
Dokumenten-Upload und -Verwaltung - Mandantenseite

Ermoeglicht Mandanten:
- Dokumente nach Kategorien hochzuladen
- Offene Anforderungen zu sehen und zu erfuellen
- Hochgeladene Dokumente einzusehen
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, List, Optional


# Dokumentkategorien fuer den Upload
UPLOAD_KATEGORIEN = {
    "persoenlich": {
        "name": "Persoenliche Dokumente",
        "icon": "person",
        "typen": [
            {"id": "personalausweis", "name": "Personalausweis / Reisepass"},
            {"id": "meldebescheinigung", "name": "Meldebescheinigung"},
        ]
    },
    "einkommen": {
        "name": "Einkommensnachweise",
        "icon": "currency-euro",
        "typen": [
            {"id": "gehaltsabrechnung", "name": "Gehaltsabrechnung"},
            {"id": "steuerbescheid", "name": "Steuerbescheid"},
            {"id": "steuererklaerung", "name": "Steuererklaerung"},
            {"id": "arbeitsvertrag", "name": "Arbeitsvertrag"},
            {"id": "rentenbescheid", "name": "Rentenbescheid"},
        ]
    },
    "familie": {
        "name": "Familienrechtliche Dokumente",
        "icon": "people",
        "typen": [
            {"id": "heiratsurkunde", "name": "Heiratsurkunde"},
            {"id": "geburtsurkunde", "name": "Geburtsurkunde"},
            {"id": "ehevertrag", "name": "Ehevertrag"},
            {"id": "trennungsvereinbarung", "name": "Trennungsvereinbarung"},
        ]
    },
    "vermoegen": {
        "name": "Vermoegen & Immobilien",
        "icon": "house",
        "typen": [
            {"id": "grundbuchauszug", "name": "Grundbuchauszug"},
            {"id": "kontoauszuege", "name": "Kontoauszuege"},
            {"id": "depotauszug", "name": "Depotauszug"},
            {"id": "kfz_papiere", "name": "KFZ-Papiere"},
            {"id": "mietvertrag", "name": "Mietvertrag"},
        ]
    },
    "kinder": {
        "name": "Dokumente zu Kindern",
        "icon": "emoji-smile",
        "typen": [
            {"id": "geburtsurkunde_kind", "name": "Geburtsurkunde Kind"},
            {"id": "kindergeldbescheid", "name": "Kindergeldbescheid"},
            {"id": "schulbescheinigung", "name": "Schulbescheinigung"},
            {"id": "ausbildungsvertrag", "name": "Ausbildungsvertrag"},
        ]
    },
    "sonstiges": {
        "name": "Sonstige Dokumente",
        "icon": "file-earmark",
        "typen": [
            {"id": "vollmacht", "name": "Vollmacht"},
            {"id": "sonstiges", "name": "Sonstige Dokumente"},
        ]
    },
}


def get_offene_anforderungen() -> List[Dict]:
    """Holt offene Dokumentenanforderungen (Demo-Daten)"""
    return [
        {
            "id": "anf_1",
            "dokument_typ": "gehaltsabrechnung_12m",
            "dokument_name": "Gehaltsabrechnungen (letzte 12 Monate)",
            "kategorie": "Einkommensnachweise",
            "beschreibung": "Bitte laden Sie alle Gehaltsabrechnungen der letzten 12 Monate hoch.",
            "frist": "24.01.2026",
            "prioritaet": "hoch",
            "status": "offen"
        },
        {
            "id": "anf_2",
            "dokument_typ": "steuerbescheid",
            "dokument_name": "Steuerbescheid",
            "kategorie": "Einkommensnachweise",
            "beschreibung": "Bitte laden Sie Ihren letzten Einkommensteuerbescheid hoch.",
            "frist": "24.01.2026",
            "prioritaet": "hoch",
            "status": "offen"
        },
        {
            "id": "anf_3",
            "dokument_typ": "grundbuchauszug",
            "dokument_name": "Grundbuchauszug",
            "kategorie": "Vermoegen & Immobilien",
            "beschreibung": "Bitte laden Sie einen aktuellen Grundbuchauszug fuer alle Immobilien hoch.",
            "frist": "24.01.2026",
            "prioritaet": "normal",
            "status": "offen"
        },
    ]


def render_mandant_dashboard():
    """Dashboard fuer Mandanten mit prominenten Benachrichtigungen"""
    user = st.session_state.user
    case = st.session_state.current_case

    st.header(f"Willkommen, {user.get('vorname')} {user.get('nachname')}")

    if case:
        st.info(f"**Ihre Akte:** {case.get('case_number')} | **Verfahrensart:** {case.get('case_type', '').title()} | **Ihr Anwalt:** {case.get('lawyer', 'N/A')}")

    st.markdown("---")

    # PROMINENTE ANZEIGE: Offene Dokumentenanforderungen
    offene_anforderungen = get_offene_anforderungen()

    if offene_anforderungen:
        st.markdown("### Offene Dokumentenanforderungen")

        # Grosse, auffaellige Warnung
        anzahl = len(offene_anforderungen)
        dringende = sum(1 for a in offene_anforderungen if a.get("prioritaet") == "hoch")

        if dringende > 0:
            st.error(f"""
            **{anzahl} Dokument(e) wurden von Ihrem Anwalt angefordert!**

            Davon sind **{dringende} dringend** - bitte laden Sie diese so schnell wie moeglich hoch.

            Klicken Sie auf die Schaltflaechen unten, um die Dokumente hochzuladen.
            """)
        else:
            st.warning(f"""
            **{anzahl} Dokument(e) wurden von Ihrem Anwalt angefordert.**

            Bitte laden Sie diese bis zur angegebenen Frist hoch.
            """)

        # Buttons fuer jedes angeforderte Dokument
        st.markdown("#### Schnellzugriff - Jetzt hochladen:")

        for anf in offene_anforderungen:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                prioritaet_icon = "DRINGEND: " if anf.get("prioritaet") == "hoch" else ""
                st.markdown(f"**{prioritaet_icon}{anf['dokument_name']}**")
                st.caption(anf.get("beschreibung", "")[:80] + "...")

            with col2:
                if anf.get("prioritaet") == "hoch":
                    st.error(f"Frist: {anf['frist']}")
                else:
                    st.warning(f"Frist: {anf['frist']}")

            with col3:
                if st.button(
                    "Hochladen",
                    key=f"dashboard_quick_{anf['id']}",
                    use_container_width=True,
                    type="primary" if anf.get("prioritaet") == "hoch" else "secondary"
                ):
                    st.session_state.upload_target = anf['id']
                    st.session_state.current_page = "Dokumente hochladen"
                    st.rerun()

            st.markdown("")

    # Uebersicht Boxen
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Offene Anforderungen",
            len(offene_anforderungen),
            delta=f"-{len(offene_anforderungen)}" if offene_anforderungen else None,
            delta_color="inverse"
        )

    with col2:
        # Demo-Daten
        st.metric("Hochgeladene Dokumente", "5")

    with col3:
        st.metric("Freigegebene Berechnungen", "2")

    st.markdown("---")

    # Letzte Aktivitaeten
    st.markdown("### Letzte Aktivitaeten")

    aktivitaeten = [
        {"zeit": "Heute, 10:30", "text": "Ihr Anwalt hat 3 Dokumente angefordert", "typ": "anforderung"},
        {"zeit": "Gestern", "text": "Neue Berechnung wurde fuer Sie freigegeben", "typ": "berechnung"},
        {"zeit": "10.01.2026", "text": "Dokument 'Gehaltsabrechnung Dez' wurde geprueft", "typ": "dokument"},
    ]

    for akt in aktivitaeten:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.caption(akt["zeit"])
        with col2:
            if akt["typ"] == "anforderung":
                st.warning(akt["text"])
            elif akt["typ"] == "berechnung":
                st.success(akt["text"])
            else:
                st.info(akt["text"])


def render_dokument_upload():
    """Seite fuer Dokumenten-Upload mit kategorisierten Reitern"""
    st.header("Dokumente hochladen")

    case = st.session_state.current_case
    if case:
        st.info(f"Akte: {case.get('case_number')} - {case.get('case_type', '').title()}")

    # Offene Anforderungen anzeigen
    offene_anforderungen = get_offene_anforderungen()

    if offene_anforderungen:
        st.markdown("### Angeforderte Dokumente")
        st.markdown("Diese Dokumente wurden von Ihrem Anwalt angefordert:")

        # Tabs fuer angeforderte Dokumente
        tab_namen = [anf["dokument_name"] for anf in offene_anforderungen]
        tab_namen.append("Weitere Dokumente")

        tabs = st.tabs(tab_namen)

        for idx, anf in enumerate(offene_anforderungen):
            with tabs[idx]:
                render_einzelner_upload(anf)

        # Tab fuer weitere Dokumente
        with tabs[-1]:
            render_allgemeiner_upload()
    else:
        st.success("Alle angeforderten Dokumente wurden eingereicht!")
        st.markdown("---")
        render_allgemeiner_upload()


def render_einzelner_upload(anforderung: Dict):
    """Rendert Upload-Bereich fuer ein einzelnes angefordertes Dokument"""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"#### {anforderung['dokument_name']}")
        st.markdown(anforderung.get('beschreibung', ''))

    with col2:
        if anforderung.get('prioritaet') == 'hoch':
            st.error(f"**Frist: {anforderung['frist']}**")
        else:
            st.warning(f"Frist: {anforderung['frist']}")

    st.markdown("---")

    # Hinweise zum Dokument
    with st.expander("Hinweise zum Upload"):
        st.markdown("""
        **Erlaubte Dateiformate:**
        - PDF (empfohlen)
        - Bilder: JPG, PNG, TIFF
        - Office: Word (DOCX), Excel (XLSX)

        **Tipps:**
        - Achten Sie auf gute Lesbarkeit
        - Alle Seiten muessen vollstaendig sein
        - Laden Sie zusammengehoerige Dokumente als eine Datei hoch
        """)

    # File Uploader
    uploaded_files = st.file_uploader(
        f"Dateien fuer '{anforderung['dokument_name']}' hochladen",
        type=["pdf", "jpg", "jpeg", "png", "tiff", "docx", "xlsx"],
        accept_multiple_files=True,
        key=f"upload_{anforderung['id']}"
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} Datei(en) ausgewaehlt")

        for file in uploaded_files:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"- {file.name}")
            with col2:
                st.caption(f"{file.size / 1024:.1f} KB")
            with col3:
                st.caption(file.type)

        # Zusaetzliche Angaben
        st.markdown("---")
        st.markdown("**Zusaetzliche Angaben (optional):**")

        col1, col2 = st.columns(2)
        with col1:
            zeitraum_von = st.date_input(
                "Zeitraum von",
                value=None,
                key=f"zeitraum_von_{anforderung['id']}"
            )
        with col2:
            zeitraum_bis = st.date_input(
                "Zeitraum bis",
                value=None,
                key=f"zeitraum_bis_{anforderung['id']}"
            )

        bemerkung = st.text_area(
            "Bemerkung",
            placeholder="Optionale Bemerkung zu diesem Dokument...",
            key=f"bemerkung_{anforderung['id']}"
        )

        # Upload-Button
        if st.button(
            "Dokumente einreichen",
            type="primary",
            key=f"submit_{anforderung['id']}",
            use_container_width=True
        ):
            with st.spinner("Dokumente werden verarbeitet und OCR wird durchgefuehrt..."):
                # Hier wuerde der echte Upload und OCR stattfinden
                import time
                time.sleep(1)

            st.success(f"""
            **Erfolgreich hochgeladen!**

            {len(uploaded_files)} Dokument(e) wurden eingereicht und werden nun von unserem System verarbeitet.
            Die Texterkennung (OCR) wird automatisch durchgefuehrt.

            Ihr Anwalt wird benachrichtigt.
            """)
            st.balloons()


def render_allgemeiner_upload():
    """Rendert allgemeinen Upload-Bereich nach Kategorien"""
    st.markdown("### Weitere Dokumente hochladen")
    st.markdown("Waehlen Sie eine Kategorie und laden Sie Ihre Dokumente hoch.")

    # Kategorie-Tabs
    kategorien = list(UPLOAD_KATEGORIEN.keys())
    kategorie_namen = [UPLOAD_KATEGORIEN[k]["name"] for k in kategorien]

    tabs = st.tabs(kategorie_namen)

    for idx, kat_key in enumerate(kategorien):
        kat = UPLOAD_KATEGORIEN[kat_key]

        with tabs[idx]:
            st.markdown(f"#### {kat['name']}")

            # Dokumenttyp auswaehlen
            dokument_typen = [t["name"] for t in kat["typen"]]
            ausgewaehlter_typ = st.selectbox(
                "Dokumenttyp",
                dokument_typen,
                key=f"typ_{kat_key}"
            )

            # File Uploader
            uploaded_files = st.file_uploader(
                "Dateien hochladen",
                type=["pdf", "jpg", "jpeg", "png", "tiff", "docx", "xlsx"],
                accept_multiple_files=True,
                key=f"files_{kat_key}"
            )

            if uploaded_files:
                st.success(f"{len(uploaded_files)} Datei(en) ausgewaehlt")

                # Zusaetzliche Angaben
                bemerkung = st.text_area(
                    "Bemerkung (optional)",
                    key=f"bem_{kat_key}"
                )

                if st.button("Hochladen", type="primary", key=f"btn_{kat_key}"):
                    st.success("Dokumente wurden hochgeladen!")


def render_meine_dokumente():
    """Zeigt hochgeladene Dokumente des Mandanten"""
    st.header("Meine Dokumente")

    case = st.session_state.current_case
    if case:
        st.info(f"Akte: {case.get('case_number')}")

    # Filter
    col1, col2 = st.columns(2)
    with col1:
        filter_kategorie = st.selectbox(
            "Kategorie",
            ["Alle"] + [UPLOAD_KATEGORIEN[k]["name"] for k in UPLOAD_KATEGORIEN]
        )
    with col2:
        filter_status = st.selectbox(
            "Status",
            ["Alle", "In Pruefung", "Akzeptiert", "Nachbesserung erforderlich"]
        )

    st.markdown("---")

    # Demo-Dokumente
    dokumente = [
        {
            "name": "Gehaltsabrechnung_Dezember_2025.pdf",
            "kategorie": "Einkommensnachweise",
            "typ": "Gehaltsabrechnung",
            "hochgeladen": "10.01.2026",
            "status": "Akzeptiert",
            "groesse": "245 KB"
        },
        {
            "name": "Gehaltsabrechnung_November_2025.pdf",
            "kategorie": "Einkommensnachweise",
            "typ": "Gehaltsabrechnung",
            "hochgeladen": "10.01.2026",
            "status": "Akzeptiert",
            "groesse": "238 KB"
        },
        {
            "name": "Heiratsurkunde.pdf",
            "kategorie": "Familienrechtliche Dokumente",
            "typ": "Heiratsurkunde",
            "hochgeladen": "08.01.2026",
            "status": "In Pruefung",
            "groesse": "1.2 MB"
        },
        {
            "name": "Mietvertrag_2020.pdf",
            "kategorie": "Vermoegen & Immobilien",
            "typ": "Mietvertrag",
            "hochgeladen": "05.01.2026",
            "status": "Nachbesserung erforderlich",
            "groesse": "890 KB",
            "hinweis": "Bitte laden Sie auch die Nebenkostenabrechnung hoch."
        },
    ]

    # Dokumente anzeigen
    for dok in dokumente:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.markdown(f"**{dok['name']}**")
                st.caption(f"{dok['kategorie']} > {dok['typ']}")

            with col2:
                st.caption(f"Hochgeladen: {dok['hochgeladen']}")
                st.caption(dok['groesse'])

            with col3:
                if dok['status'] == "Akzeptiert":
                    st.success(dok['status'])
                elif dok['status'] == "In Pruefung":
                    st.info(dok['status'])
                else:
                    st.warning(dok['status'])

            with col4:
                st.button("Ansehen", key=f"view_{dok['name']}", use_container_width=True)

            if dok.get('hinweis'):
                st.warning(f"Hinweis: {dok['hinweis']}")

            st.markdown("---")


def render_freigegebene_berechnungen():
    """Zeigt vom Anwalt freigegebene Berechnungen"""
    st.header("Freigegebene Berechnungen")

    case = st.session_state.current_case
    if case:
        st.info(f"Akte: {case.get('case_number')}")

    st.markdown("---")

    # Demo-Berechnungen
    berechnungen = [
        {
            "titel": "Kindesunterhalt-Berechnung",
            "erstellt": "08.01.2026",
            "typ": "Kindesunterhalt",
            "ergebnis": "Der monatliche Zahlbetrag betraegt 579,00 EUR",
            "anmerkung": "Basierend auf den aktuellen Einkommensnachweisen"
        },
        {
            "titel": "Trennungsunterhalt-Berechnung (vorlaeufig)",
            "erstellt": "05.01.2026",
            "typ": "Trennungsunterhalt",
            "ergebnis": "Vorlaeufiger Anspruch: 850,00 EUR monatlich",
            "anmerkung": "Endgueltige Berechnung nach Eingang aller Unterlagen"
        },
    ]

    for ber in berechnungen:
        with st.expander(f"{ber['titel']} ({ber['erstellt']})", expanded=True):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Typ:** {ber['typ']}")
                st.markdown(f"**Ergebnis:** {ber['ergebnis']}")
                if ber.get('anmerkung'):
                    st.info(ber['anmerkung'])

            with col2:
                st.button("Details anzeigen", key=f"detail_{ber['titel']}", use_container_width=True)
                st.button("PDF herunterladen", key=f"pdf_{ber['titel']}", use_container_width=True)

            st.markdown("---")

            # Kommentar/Korrekturvorschlag
            st.markdown("**Haben Sie Anmerkungen oder Korrekturvorschlaege?**")

            korrektur = st.text_area(
                "Ihr Kommentar",
                placeholder="Falls Sie Fehler bemerken oder Anmerkungen haben, teilen Sie diese hier mit...",
                key=f"korrektur_{ber['titel']}"
            )

            if st.button("Kommentar senden", key=f"send_{ber['titel']}"):
                if korrektur:
                    st.success("Ihr Kommentar wurde an Ihren Anwalt gesendet.")
                else:
                    st.warning("Bitte geben Sie einen Kommentar ein.")
