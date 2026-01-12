"""
Ehegattenunterhalt-Rechner Seite

Streamlit-Seite für die Berechnung des Ehegattenunterhalts
(Trennungs- und nachehelicher Unterhalt).
"""

import streamlit as st
from typing import Optional

from src.calculators.ehegattenunterhalt import (
    EhegattenunterhaltRechner,
    Ehegatte,
    Unterhaltstyp,
    EhegattenunterhaltErgebnis,
)


def render_ehegattenunterhalt_page():
    """Rendert die Ehegattenunterhalt-Seite"""
    st.header("Ehegattenunterhalt-Berechnung")
    st.markdown("Trennungs- und nachehelicher Unterhalt")

    # Unterhaltsart wählen
    unterhaltsart = st.radio(
        "Art des Unterhalts",
        ["Trennungsunterhalt (§ 1361 BGB)", "Nachehelicher Unterhalt (§§ 1569 ff. BGB)"],
        horizontal=True
    )

    ist_trennungsunterhalt = "Trennungsunterhalt" in unterhaltsart

    st.markdown("---")

    # Zwei-Spalten-Layout für die Ehegatten
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Unterhaltspflichtiger")
        pflichtiger = render_ehegatte_formular("pflichtiger")

    with col2:
        st.subheader("Unterhaltsberechtigter")
        berechtigter = render_ehegatte_formular("berechtigter")

    st.markdown("---")

    # Bei nachehelichem Unterhalt: Tatbestände prüfen
    tatbestaende = None
    if not ist_trennungsunterhalt:
        st.subheader("Unterhaltstatbestände (§§ 1570-1576 BGB)")
        tatbestaende = render_tatbestaende_formular()

    # Berechnung durchführen
    st.markdown("---")

    if st.button("Berechnung durchführen", type="primary", use_container_width=True):
        with st.spinner("Berechne..."):
            ergebnis = fuehre_berechnung_durch(
                pflichtiger,
                berechtigter,
                ist_trennungsunterhalt,
                tatbestaende
            )

            if ergebnis:
                zeige_ergebnis(ergebnis)


def render_ehegatte_formular(prefix: str) -> Ehegatte:
    """Rendert das Eingabeformular für einen Ehegatten"""
    name = st.text_input(
        "Name",
        value="Ehegatte" if prefix == "pflichtiger" else "Ehegatte/in",
        key=f"{prefix}_name"
    )

    erwerbstaetig = st.checkbox(
        "Erwerbstätig",
        value=True if prefix == "pflichtiger" else False,
        key=f"{prefix}_erwerbstaetig"
    )

    col1, col2 = st.columns(2)

    with col1:
        brutto = st.number_input(
            "Bruttoeinkommen",
            min_value=0.0,
            value=4500.0 if prefix == "pflichtiger" else 0.0,
            step=100.0,
            key=f"{prefix}_brutto"
        )

    with col2:
        netto = st.number_input(
            "Nettoeinkommen",
            min_value=0.0,
            value=3200.0 if prefix == "pflichtiger" else 0.0,
            step=100.0,
            key=f"{prefix}_netto"
        )

    # Erweiterte Optionen
    with st.expander("Weitere Einkünfte"):
        sonstige = st.number_input(
            "Sonstige Einkünfte (Miete, Kapital etc.)",
            min_value=0.0,
            value=0.0,
            step=50.0,
            key=f"{prefix}_sonstige"
        )

        wohnvorteil = st.number_input(
            "Wohnvorteil (eigene Immobilie)",
            min_value=0.0,
            value=0.0,
            step=50.0,
            help="Objektiver Mietwert abzgl. Belastungen",
            key=f"{prefix}_wohnvorteil"
        )

        kindesunterhalt = st.number_input(
            "Zahlbetrag Kindesunterhalt",
            min_value=0.0,
            value=0.0,
            step=50.0,
            help="Vorrangiger Kindesunterhalt wird abgezogen",
            key=f"{prefix}_kindesunterhalt"
        )

    return Ehegatte(
        name=name,
        erwerbstaetig=erwerbstaetig,
        bruttoeinkommen=brutto,
        nettoeinkommen=netto,
        sonstige_einkuenfte=sonstige,
        wohnvorteil=wohnvorteil,
        kindesunterhalt_zahlbetrag=kindesunterhalt,
    )


def render_tatbestaende_formular() -> dict:
    """Rendert das Formular für die Unterhaltstatbestände"""
    st.markdown("""
    Für nachehelichen Unterhalt muss mindestens ein Tatbestand erfüllt sein.
    Der Grundsatz der Eigenverantwortung gilt (§ 1569 BGB).
    """)

    col1, col2 = st.columns(2)

    with col1:
        betreuung = st.checkbox(
            "§ 1570 - Betreuungsunterhalt",
            help="Betreuung eines Kindes unter 3 Jahren",
            key="tb_betreuung"
        )

        alter = st.checkbox(
            "§ 1571 - Altersunterhalt",
            help="Alter bei Scheidung/Ende Kindesbetreuung",
            key="tb_alter"
        )

        krankheit = st.checkbox(
            "§ 1572 - Krankheitsunterhalt",
            help="Krankheit oder Gebrechen",
            key="tb_krankheit"
        )

        erwerbslos = st.checkbox(
            "§ 1573 Abs. 1 - Erwerbslosigkeitsunterhalt",
            help="Keine angemessene Erwerbstätigkeit",
            key="tb_erwerbslos"
        )

    with col2:
        aufstockung = st.checkbox(
            "§ 1573 Abs. 2 - Aufstockungsunterhalt",
            help="Einkünfte reichen nicht aus",
            key="tb_aufstockung"
        )

        ausbildung = st.checkbox(
            "§ 1574 - Ausbildungsunterhalt",
            help="Ausbildung/Fortbildung/Umschulung",
            key="tb_ausbildung"
        )

        billigkeit = st.checkbox(
            "§ 1576 - Billigkeitsunterhalt",
            help="Schwerwiegende Billigkeitsgründe",
            key="tb_billigkeit"
        )

    billigkeitsgruende = ""
    if billigkeit:
        billigkeitsgruende = st.text_area(
            "Begründung für Billigkeitsunterhalt",
            key="billigkeitsgruende"
        )

    alter_bei_scheidung = None
    if alter:
        alter_bei_scheidung = st.number_input(
            "Alter bei Scheidung",
            min_value=18,
            max_value=100,
            value=65,
            key="alter_scheidung"
        )

    return {
        "kinder_unter_3": betreuung,
        "alter_bei_scheidung": alter_bei_scheidung if alter else None,
        "krankheit_gebrechen": krankheit,
        "keine_angemessene_arbeit": erwerbslos,
        "ausbildung_fortbildung": ausbildung,
        "billigkeitsgruende": billigkeitsgruende,
    }


def fuehre_berechnung_durch(
    pflichtiger: Ehegatte,
    berechtigter: Ehegatte,
    ist_trennungsunterhalt: bool,
    tatbestaende_params: Optional[dict]
) -> Optional[EhegattenunterhaltErgebnis]:
    """Führt die Berechnung durch"""
    rechner = EhegattenunterhaltRechner()

    if ist_trennungsunterhalt:
        return rechner.berechne_trennungsunterhalt(pflichtiger, berechtigter)
    else:
        # Tatbestände prüfen
        tatbestaende = rechner.pruefe_unterhalts_tatbestaende(
            berechtigter,
            **tatbestaende_params
        )
        return rechner.berechne_nachehelichen_unterhalt(
            pflichtiger,
            berechtigter,
            tatbestaende
        )


def zeige_ergebnis(ergebnis: EhegattenunterhaltErgebnis):
    """Zeigt das Berechnungsergebnis an"""
    st.markdown("---")
    st.markdown("### Berechnungsergebnis")

    # Typ anzeigen
    typ_text = (
        "Trennungsunterhalt (§ 1361 BGB)"
        if ergebnis.unterhaltstyp == Unterhaltstyp.TRENNUNGSUNTERHALT
        else "Nachehelicher Unterhalt (§§ 1569 ff. BGB)"
    )
    st.markdown(f"**{typ_text}**")

    # Hauptergebnis
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            f"Einkommen {ergebnis.pflichtiger}",
            f"{ergebnis.einkommen_pflichtiger:,.2f} €"
        )

    with col2:
        st.metric(
            f"Einkommen {ergebnis.berechtigter}",
            f"{ergebnis.einkommen_berechtigter:,.2f} €"
        )

    with col3:
        st.metric(
            "Differenz",
            f"{ergebnis.differenz:,.2f} €"
        )

    st.markdown("---")

    # Unterhaltsberechnung
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Quote:** {ergebnis.quote * 100:.0f}%")
        st.markdown(f"**Erwerbstätigenbonus:** {ergebnis.erwerbstaetigenbonus:,.2f} €")

    with col2:
        st.markdown(f"**Unterhalt (berechnet):** {ergebnis.unterhalt_vor_selbstbehalt:,.2f} €")
        st.markdown(f"**Selbstbehalt:** {ergebnis.selbstbehalt:,.2f} €")

    # Endergebnis
    st.markdown("---")

    if ergebnis.selbstbehalt_unterschritten:
        st.warning(
            f"Selbstbehalt unterschritten - Unterhalt auf "
            f"{ergebnis.unterhalt_nach_selbstbehalt:,.2f} € reduziert"
        )

    st.success(
        f"**Zahlbetrag Ehegattenunterhalt: {ergebnis.unterhalt_nach_selbstbehalt:,.2f} € / Monat**"
    )

    # Bei nachehelichem Unterhalt: Tatbestände anzeigen
    if ergebnis.tatbestaende:
        st.markdown("---")
        st.markdown("### Geprüfte Tatbestände")

        erfuellt = [tb for tb in ergebnis.tatbestaende if tb.erfuellt]
        nicht_erfuellt = [tb for tb in ergebnis.tatbestaende if not tb.erfuellt]

        if erfuellt:
            st.markdown("**Erfüllt:**")
            for tb in erfuellt:
                st.markdown(f"- ✓ {tb.paragraph}: {tb.bezeichnung}")
                if tb.begruendung:
                    st.markdown(f"  *{tb.begruendung}*")
        else:
            st.error(
                "Kein Unterhaltstatbestand erfüllt. "
                "Grundsatz der Eigenverantwortung gilt."
            )

        with st.expander("Nicht erfüllte Tatbestände"):
            for tb in nicht_erfuellt:
                st.markdown(f"- ✗ {tb.paragraph}: {tb.bezeichnung}")

    # Hinweise
    if ergebnis.hinweise:
        st.markdown("---")
        st.markdown("### Hinweise")
        for hinweis in ergebnis.hinweise:
            st.info(hinweis)

    # Details
    with st.expander("Berechnungsdetails"):
        st.json(ergebnis.berechnungsdetails)
