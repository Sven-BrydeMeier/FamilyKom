"""
Kindesunterhalt-Rechner Seite

Streamlit-Seite für die Berechnung des Kindesunterhalts
nach der Düsseldorfer Tabelle.
"""

import streamlit as st
from datetime import date, datetime
from typing import List

from src.calculators.kindesunterhalt import (
    KindesunterhaltRechner,
    Kind,
    Einkommensbereinigung,
    GesamtErgebnis,
)
from config.constants import KINDERGELD_2025


def render_kindesunterhalt_page():
    """Rendert die Kindesunterhalt-Seite"""
    st.header("Kindesunterhalt-Berechnung")
    st.markdown("Nach Düsseldorfer Tabelle 2025")

    # Tabs für verschiedene Bereiche
    tab_eingabe, tab_ergebnis, tab_info = st.tabs([
        "Eingabe",
        "Berechnung",
        "Informationen"
    ])

    with tab_eingabe:
        render_eingabe_formular()

    with tab_ergebnis:
        render_berechnung()

    with tab_info:
        render_informationen()


def render_eingabe_formular():
    """Rendert das Eingabeformular"""
    st.subheader("Einkommensdaten des Pflichtigen")

    col1, col2 = st.columns(2)

    with col1:
        brutto = st.number_input(
            "Bruttoeinkommen (monatlich)",
            min_value=0.0,
            value=4500.0,
            step=100.0,
            format="%.2f",
            help="Durchschnittliches monatliches Bruttoeinkommen"
        )

        netto = st.number_input(
            "Nettoeinkommen (monatlich)",
            min_value=0.0,
            value=3200.0,
            step=100.0,
            format="%.2f",
            help="Durchschnittliches monatliches Nettoeinkommen"
        )

    with col2:
        erwerbstaetig = st.checkbox("Erwerbstätig", value=True)

        berufsbedingte_pauschal = st.checkbox(
            "Berufsbedingte Aufwendungen pauschal (5%)",
            value=True,
            help="5% des Netto, mind. 50€, max. 150€"
        )

        if not berufsbedingte_pauschal:
            berufsbedingte = st.number_input(
                "Berufsbedingte Aufwendungen (tatsächlich)",
                min_value=0.0,
                value=150.0,
                step=10.0
            )
        else:
            berufsbedingte = None

    st.markdown("---")
    st.subheader("Weitere Abzüge")

    col3, col4 = st.columns(2)

    with col3:
        fahrtkosten = st.number_input(
            "Fahrtkosten zur Arbeit",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Nur wenn nicht in Pauschale enthalten"
        )

        private_av = st.number_input(
            "Private Altersvorsorge",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Max. 4% des Bruttoeinkommens"
        )

    with col4:
        schulden = st.number_input(
            "Schuldenverbindlichkeiten",
            min_value=0.0,
            value=0.0,
            step=50.0,
            help="Ehebedingte Schulden"
        )

        vorrangig = st.number_input(
            "Vorrangige Unterhaltslasten",
            min_value=0.0,
            value=0.0,
            step=50.0,
            help="z.B. Unterhalt für andere Kinder"
        )

    # Speichern in Session State
    st.session_state.kindesunterhalt_eingabe = {
        "brutto": brutto,
        "netto": netto,
        "erwerbstaetig": erwerbstaetig,
        "berufsbedingte": berufsbedingte,
        "fahrtkosten": fahrtkosten,
        "private_av": private_av,
        "schulden": schulden,
        "vorrangig": vorrangig,
    }

    st.markdown("---")
    st.subheader("Kinder")

    render_kinder_eingabe()


def render_kinder_eingabe():
    """Rendert die Eingabe für Kinder"""
    if "kinder_liste" not in st.session_state:
        st.session_state.kinder_liste = []

    # Neues Kind hinzufügen
    with st.expander("Kind hinzufügen", expanded=len(st.session_state.kinder_liste) == 0):
        col1, col2 = st.columns(2)

        with col1:
            kind_name = st.text_input("Name des Kindes", key="neues_kind_name")
            geburtsdatum = st.date_input(
                "Geburtsdatum",
                value=date(2015, 6, 15),
                min_value=date(1990, 1, 1),
                max_value=date.today(),
                key="neues_kind_geb"
            )

        with col2:
            lebt_bei_pflichtigem = st.checkbox(
                "Lebt beim Pflichtigen",
                value=False,
                key="neues_kind_lebt"
            )

            eigenes_einkommen = st.number_input(
                "Eigenes Einkommen (bei Volljährigen)",
                min_value=0.0,
                value=0.0,
                step=50.0,
                key="neues_kind_einkommen"
            )

        if st.button("Kind hinzufügen"):
            if kind_name:
                neues_kind = {
                    "name": kind_name,
                    "geburtsdatum": geburtsdatum,
                    "lebt_bei_pflichtigem": lebt_bei_pflichtigem,
                    "eigenes_einkommen": eigenes_einkommen,
                }
                st.session_state.kinder_liste.append(neues_kind)
                st.rerun()
            else:
                st.warning("Bitte Namen eingeben")

    # Liste der Kinder anzeigen
    if st.session_state.kinder_liste:
        st.markdown("**Eingetragene Kinder:**")

        for i, kind in enumerate(st.session_state.kinder_liste):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                # Alter berechnen
                heute = date.today()
                geb = kind["geburtsdatum"]
                alter = heute.year - geb.year
                if (heute.month, heute.day) < (geb.month, geb.day):
                    alter -= 1

                st.markdown(
                    f"**{kind['name']}** - {alter} Jahre "
                    f"(geb. {geb.strftime('%d.%m.%Y')})"
                )

            with col2:
                if kind.get("eigenes_einkommen", 0) > 0:
                    st.markdown(f"Einkommen: {kind['eigenes_einkommen']:.0f}€")

            with col3:
                if st.button("Entfernen", key=f"remove_kind_{i}"):
                    st.session_state.kinder_liste.pop(i)
                    st.rerun()


def render_berechnung():
    """Rendert die Berechnung und das Ergebnis"""
    st.subheader("Berechnungsergebnis")

    # Prüfen ob Daten vorhanden
    if "kindesunterhalt_eingabe" not in st.session_state:
        st.info("Bitte geben Sie zunächst die Einkommensdaten ein.")
        return

    if not st.session_state.get("kinder_liste"):
        st.info("Bitte fügen Sie mindestens ein Kind hinzu.")
        return

    eingabe = st.session_state.kindesunterhalt_eingabe
    kinder_daten = st.session_state.kinder_liste

    # Weitere Unterhaltsberechtigte (z.B. Ehegatte)
    weitere_berechtigte = st.number_input(
        "Weitere Unterhaltsberechtigte (z.B. Ehegatte)",
        min_value=0,
        value=0,
        step=1,
        help="Für Gruppenanpassung in der Tabelle"
    )

    if st.button("Berechnung durchführen", type="primary"):
        with st.spinner("Berechne..."):
            ergebnis = fuehre_berechnung_durch(
                eingabe, kinder_daten, weitere_berechtigte
            )

            if ergebnis:
                st.session_state.kindesunterhalt_ergebnis = ergebnis
                zeige_ergebnis(ergebnis)


def fuehre_berechnung_durch(
    eingabe: dict,
    kinder_daten: list,
    weitere_berechtigte: int
) -> GesamtErgebnis:
    """Führt die Berechnung durch"""
    # Einkommensbereinigung erstellen
    einkommen = Einkommensbereinigung(
        bruttoeinkommen=eingabe["brutto"],
        nettoeinkommen=eingabe["netto"],
        berufsbedingte_aufwendungen=eingabe.get("berufsbedingte"),
        fahrtkosten=eingabe.get("fahrtkosten", 0),
        private_altersvorsorge=eingabe.get("private_av", 0),
        schulden=eingabe.get("schulden", 0),
        vorrangige_unterhaltslasten=eingabe.get("vorrangig", 0),
    )

    # Kind-Objekte erstellen
    kinder = []
    for kind_data in kinder_daten:
        kind = Kind(
            name=kind_data["name"],
            geburtsdatum=kind_data["geburtsdatum"],
            lebt_bei_pflichtigem=kind_data.get("lebt_bei_pflichtigem", False),
            eigenes_einkommen=kind_data.get("eigenes_einkommen", 0),
        )
        kinder.append(kind)

    # Rechner erstellen und berechnen
    rechner = KindesunterhaltRechner()
    ergebnis = rechner.berechne(
        einkommen=einkommen,
        kinder=kinder,
        erwerbstaetig=eingabe.get("erwerbstaetig", True),
        weitere_unterhaltsberechtigte=weitere_berechtigte
    )

    return ergebnis


def zeige_ergebnis(ergebnis: GesamtErgebnis):
    """Zeigt das Berechnungsergebnis an"""
    # Übersicht
    st.markdown("---")
    st.markdown("### Zusammenfassung")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Bereinigtes Nettoeinkommen",
            f"{ergebnis.bereinigtes_einkommen:,.2f} €"
        )

    with col2:
        gruppe_text = f"Gruppe {ergebnis.einkommensgruppe}"
        if ergebnis.gruppenanpassung != 0:
            gruppe_text += f" → {ergebnis.einkommensgruppe + ergebnis.gruppenanpassung}"
        st.metric("Einkommensgruppe", gruppe_text)

    with col3:
        st.metric(
            "Gesamtunterhalt",
            f"{ergebnis.gesamtunterhalt:,.2f} €"
        )

    # Warnung bei Mangelfall
    if ergebnis.ist_mangelfall:
        st.error(
            "**Mangelfall**: Der Selbstbehalt kann nicht gewahrt werden. "
            "Die Zahlbeträge wurden anteilig reduziert."
        )

    # Details je Kind
    st.markdown("---")
    st.markdown("### Unterhalt je Kind")

    for kind_ergebnis in ergebnis.kinder_ergebnisse:
        with st.expander(
            f"{kind_ergebnis.kind_name} - {kind_ergebnis.zahlbetrag:,.2f} €/Monat",
            expanded=True
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Alter:** {kind_ergebnis.alter} Jahre")
                st.markdown(f"**Altersstufe:** {kind_ergebnis.altersstufe + 1}")
                st.markdown(f"**Einkommensgruppe:** {kind_ergebnis.angepasste_gruppe}")

            with col2:
                st.markdown(f"**Tabellenbetrag:** {kind_ergebnis.tabellenbetrag:,.2f} €")
                st.markdown(f"**Kindergeldabzug:** {kind_ergebnis.kindergeldabzug:,.2f} €")
                st.markdown(f"**Zahlbetrag:** {kind_ergebnis.zahlbetrag:,.2f} €")

            if kind_ergebnis.hinweise:
                for hinweis in kind_ergebnis.hinweise:
                    st.warning(hinweis)

    # Selbstbehalt
    st.markdown("---")
    st.markdown("### Selbstbehaltsprüfung")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Verbleibendes Einkommen:** {ergebnis.verbleibendes_einkommen:,.2f} €")

    with col2:
        st.markdown(f"**Selbstbehalt:** {ergebnis.selbstbehalt:,.2f} €")

    if ergebnis.verbleibendes_einkommen >= ergebnis.selbstbehalt:
        st.success("Selbstbehalt wird gewahrt.")
    else:
        differenz = ergebnis.selbstbehalt - ergebnis.verbleibendes_einkommen
        st.error(f"Selbstbehalt wird um {differenz:,.2f} € unterschritten.")


def render_informationen():
    """Rendert die Informationsseite"""
    st.subheader("Informationen zur Berechnung")

    st.markdown("""
    ### Düsseldorfer Tabelle 2025

    Die Düsseldorfer Tabelle ist eine Richtlinie zur Berechnung des Kindesunterhalts.
    Sie wird jährlich vom OLG Düsseldorf aktualisiert.

    #### Altersstufen

    | Stufe | Alter | Bezeichnung |
    |-------|-------|-------------|
    | 1 | 0-5 Jahre | Kleinkind |
    | 2 | 6-11 Jahre | Schulkind |
    | 3 | 12-17 Jahre | Teenager |
    | 4 | ab 18 Jahre | Volljährig |

    #### Selbstbehalt 2025

    | Situation | Erwerbstätig | Nicht erwerbstätig |
    |-----------|--------------|-------------------|
    | Minderjährige Kinder | 1.450 € | 1.200 € |
    | Volljährige Kinder | 1.750 € | 1.750 € |

    #### Kindergeld 2025
    """)

    st.info(f"Kindergeld: {KINDERGELD_2025} € pro Kind")

    st.markdown("""
    Bei **minderjährigen** Kindern wird das **hälftige** Kindergeld vom Tabellenbetrag abgezogen.
    Bei **volljährigen** Kindern wird das **volle** Kindergeld abgezogen.

    #### Einkommensbereinigung

    Vom Nettoeinkommen werden abgezogen:
    - Berufsbedingte Aufwendungen (pauschal 5%, mind. 50€, max. 150€)
    - Fahrtkosten zur Arbeit
    - Private Altersvorsorge (max. 4% vom Brutto)
    - Ehebedingte Schulden
    - Vorrangige Unterhaltslasten
    """)
