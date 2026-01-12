"""
Zugewinnausgleich-Rechner Seite

Streamlit-Seite für die Berechnung des Zugewinnausgleichs.
"""

import streamlit as st
from datetime import date
from typing import List

from src.calculators.zugewinn import (
    ZugewinnausgleichRechner,
    EhegattenVermoegen,
    Vermoegensgegenstand,
    PrivilegierterErwerb,
    ZugewinnErgebnis,
)


def render_zugewinn_page():
    """Rendert die Zugewinnausgleich-Seite"""
    st.header("Zugewinnausgleich-Berechnung")
    st.markdown("Nach §§ 1373 ff. BGB")

    # Stichtage
    st.subheader("Stichtage")
    col1, col2 = st.columns(2)

    with col1:
        heiratsdatum = st.date_input(
            "Datum der Eheschließung",
            value=date(2010, 6, 15),
            min_value=date(1950, 1, 1),
            max_value=date.today(),
            key="heiratsdatum"
        )

    with col2:
        endstichtag = st.date_input(
            "Endstichtag (Zustellung Scheidungsantrag)",
            value=date.today(),
            min_value=heiratsdatum,
            max_value=date.today(),
            key="endstichtag"
        )

    st.markdown("---")

    # Tabs für beide Ehegatten
    tab1, tab2 = st.tabs(["Ehegatte A", "Ehegatte B"])

    with tab1:
        ehegatte_a = render_vermoegen_formular("a")

    with tab2:
        ehegatte_b = render_vermoegen_formular("b")

    # Berechnung
    st.markdown("---")

    if st.button("Zugewinnausgleich berechnen", type="primary", use_container_width=True):
        with st.spinner("Berechne..."):
            rechner = ZugewinnausgleichRechner()
            ergebnis = rechner.berechne(
                ehegatte_a,
                ehegatte_b,
                heiratsdatum,
                endstichtag
            )
            zeige_ergebnis(ergebnis)


def render_vermoegen_formular(prefix: str) -> EhegattenVermoegen:
    """Rendert das Vermögensformular für einen Ehegatten"""
    name = st.text_input(
        "Name",
        value=f"Ehegatte {'A' if prefix == 'a' else 'B'}",
        key=f"name_{prefix}"
    )

    # Anfangsvermögen
    st.markdown("#### Anfangsvermögen (bei Eheschließung)")

    col1, col2 = st.columns(2)

    with col1:
        anfang_aktiva = st.number_input(
            "Aktiva (Vermögenswerte)",
            min_value=0.0,
            value=20000.0 if prefix == "a" else 5000.0,
            step=1000.0,
            key=f"anfang_aktiva_{prefix}",
            help="Summe aller Vermögenswerte bei Eheschließung"
        )

    with col2:
        anfang_passiva = st.number_input(
            "Passiva (Verbindlichkeiten)",
            min_value=0.0,
            value=5000.0 if prefix == "a" else 0.0,
            step=1000.0,
            key=f"anfang_passiva_{prefix}",
            help="Summe aller Schulden bei Eheschließung"
        )

    # Privilegierte Erwerbe
    st.markdown("#### Privilegierte Erwerbe (während der Ehe)")
    st.markdown("*Erbschaften und Schenkungen werden dem Anfangsvermögen hinzugerechnet*")

    privilegiert_summe = st.number_input(
        "Summe privilegierter Erwerbe",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        key=f"privilegiert_{prefix}",
        help="Erbschaften, Schenkungen (§ 1374 Abs. 2 BGB)"
    )

    # Endvermögen
    st.markdown("#### Endvermögen (zum Stichtag)")

    col1, col2 = st.columns(2)

    with col1:
        end_aktiva = st.number_input(
            "Aktiva (Vermögenswerte)",
            min_value=0.0,
            value=150000.0 if prefix == "a" else 80000.0,
            step=1000.0,
            key=f"end_aktiva_{prefix}",
            help="Summe aller Vermögenswerte zum Stichtag"
        )

    with col2:
        end_passiva = st.number_input(
            "Passiva (Verbindlichkeiten)",
            min_value=0.0,
            value=50000.0 if prefix == "a" else 10000.0,
            step=1000.0,
            key=f"end_passiva_{prefix}",
            help="Summe aller Schulden zum Stichtag"
        )

    # Vermögensobjekt erstellen
    anfangsvermoegen = []
    if anfang_aktiva > 0:
        anfangsvermoegen.append(Vermoegensgegenstand(
            bezeichnung="Anfangsvermögen (gesamt)",
            wert=anfang_aktiva,
            stichtag=date.today(),  # Wird nicht verwendet
            kategorie="sonstig"
        ))

    endvermoegen = []
    if end_aktiva > 0:
        endvermoegen.append(Vermoegensgegenstand(
            bezeichnung="Endvermögen (gesamt)",
            wert=end_aktiva,
            stichtag=date.today(),
            kategorie="sonstig"
        ))

    privilegierte_erwerbe = []
    if privilegiert_summe > 0:
        privilegierte_erwerbe.append(PrivilegierterErwerb(
            bezeichnung="Privilegierte Erwerbe (gesamt)",
            wert=privilegiert_summe,
            erwerbsdatum=date.today(),
            erwerbsart="erbschaft"
        ))

    return EhegattenVermoegen(
        name=name,
        anfangsvermoegen=anfangsvermoegen,
        anfangsverbindlichkeiten=anfang_passiva,
        endvermoegen=endvermoegen,
        endverbindlichkeiten=end_passiva,
        privilegierte_erwerbe=privilegierte_erwerbe
    )


def zeige_ergebnis(ergebnis: ZugewinnErgebnis):
    """Zeigt das Berechnungsergebnis an"""
    st.markdown("---")
    st.markdown("### Berechnungsergebnis")

    # Indexierung
    st.markdown(f"""
    **Indexierung:**
    - VPI Heirat: {ergebnis.vpi_heirat:.1f}
    - VPI Endstichtag: {ergebnis.vpi_endstichtag:.1f}
    - Faktor: {ergebnis.indexierungsfaktor:.4f}
    (+{ergebnis.berechnungsdetails.get('inflation_prozent', 0):.1f}% Inflation)
    """)

    st.markdown("---")

    # Vergleichstabelle
    col_header, col_a, col_b = st.columns([2, 1, 1])

    with col_header:
        st.markdown("**Position**")
    with col_a:
        st.markdown(f"**{ergebnis.ehegatte_a}**")
    with col_b:
        st.markdown(f"**{ergebnis.ehegatte_b}**")

    # Anfangsvermögen
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("Anfangsvermögen (Nominal)")
    with col2:
        st.markdown(f"{ergebnis.anfangsvermoegen_a:,.2f} €")
    with col3:
        st.markdown(f"{ergebnis.anfangsvermoegen_b:,.2f} €")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("Anfangsvermögen (indexiert)")
    with col2:
        st.markdown(f"{ergebnis.anfangsvermoegen_a_indexiert:,.2f} €")
    with col3:
        st.markdown(f"{ergebnis.anfangsvermoegen_b_indexiert:,.2f} €")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("+ Privilegierte Erwerbe")
    with col2:
        st.markdown(f"{ergebnis.privilegierte_erwerbe_a:,.2f} €")
    with col3:
        st.markdown(f"{ergebnis.privilegierte_erwerbe_b:,.2f} €")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**Endvermögen**")
    with col2:
        st.markdown(f"**{ergebnis.endvermoegen_a:,.2f} €**")
    with col3:
        st.markdown(f"**{ergebnis.endvermoegen_b:,.2f} €**")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**ZUGEWINN**")
    with col2:
        st.markdown(f"**{ergebnis.zugewinn_a:,.2f} €**")
    with col3:
        st.markdown(f"**{ergebnis.zugewinn_b:,.2f} €**")

    # Ausgleich
    st.markdown("---")
    st.markdown("### Ausgleichsanspruch")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Differenz der Zugewinne", f"{ergebnis.differenz:,.2f} €")

    with col2:
        st.metric("Ausgleichsanspruch (50%)", f"{ergebnis.ausgleichsanspruch:,.2f} €")

    # Ergebnis
    if ergebnis.ausgleichsberechtigt:
        st.success(
            f"**{ergebnis.ausgleichsverpflichtet}** schuldet "
            f"**{ergebnis.ausgleichsberechtigt}** einen Ausgleich von "
            f"**{ergebnis.ausgleichsanspruch:,.2f} €**"
        )
    else:
        st.info("Beide Ehegatten haben den gleichen Zugewinn. Kein Ausgleich erforderlich.")

    # Hinweise
    if ergebnis.hinweise:
        st.markdown("---")
        st.markdown("### Hinweise")
        for hinweis in ergebnis.hinweise:
            st.info(hinweis)

    # Details
    with st.expander("Berechnungsdetails"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{ergebnis.ehegatte_a}:**")
            st.markdown(f"- Aktiva Anfang: {ergebnis.berechnungsdetails.get('aktiva_a', 0):,.2f} €")
            st.markdown(f"- Passiva Anfang: {ergebnis.berechnungsdetails.get('passiva_a', 0):,.2f} €")
            st.markdown(f"- Aktiva Ende: {ergebnis.berechnungsdetails.get('endaktiva_a', 0):,.2f} €")
            st.markdown(f"- Passiva Ende: {ergebnis.berechnungsdetails.get('endpassiva_a', 0):,.2f} €")

        with col2:
            st.markdown(f"**{ergebnis.ehegatte_b}:**")
            st.markdown(f"- Aktiva Anfang: {ergebnis.berechnungsdetails.get('aktiva_b', 0):,.2f} €")
            st.markdown(f"- Passiva Anfang: {ergebnis.berechnungsdetails.get('passiva_b', 0):,.2f} €")
            st.markdown(f"- Aktiva Ende: {ergebnis.berechnungsdetails.get('endaktiva_b', 0):,.2f} €")
            st.markdown(f"- Passiva Ende: {ergebnis.berechnungsdetails.get('endpassiva_b', 0):,.2f} €")

        st.markdown(f"**Ehedauer:** {ergebnis.berechnungsdetails.get('ehedauer_jahre', 0):.1f} Jahre")
