"""
RVG-Gebührenrechner Seite

Streamlit-Seite für die Berechnung von Rechtsanwaltsgebühren.
"""

import streamlit as st

from src.calculators.rvg import (
    RVGRechner,
    RVGErgebnis,
    Verfahrensart,
)


def render_rvg_page():
    """Rendert die RVG-Gebührenrechner-Seite"""
    st.header("RVG-Gebührenberechnung")
    st.markdown("Rechtsanwaltsvergütung nach RVG (Stand 01.06.2025)")

    # Berechnungsart wählen
    berechnungsart = st.radio(
        "Berechnungsart",
        [
            "Scheidungsverfahren",
            "Außergerichtliche Vertretung",
            "Gerichtliche Vertretung",
            "Erstberatung",
        ],
        horizontal=True
    )

    st.markdown("---")

    if berechnungsart == "Scheidungsverfahren":
        render_scheidung()
    elif berechnungsart == "Außergerichtliche Vertretung":
        render_aussergericht()
    elif berechnungsart == "Gerichtliche Vertretung":
        render_gerichtlich()
    elif berechnungsart == "Erstberatung":
        render_erstberatung()


def render_scheidung():
    """Rendert das Scheidungsformular"""
    st.subheader("Scheidungsverfahren mit Folgesachen")

    st.markdown("#### Einkommen der Ehegatten")

    col1, col2 = st.columns(2)

    with col1:
        netto_a = st.number_input(
            "Nettoeinkommen Ehegatte A",
            min_value=0.0,
            value=3500.0,
            step=100.0,
            help="Monatliches Nettoeinkommen"
        )

    with col2:
        netto_b = st.number_input(
            "Nettoeinkommen Ehegatte B",
            min_value=0.0,
            value=1500.0,
            step=100.0,
            help="Monatliches Nettoeinkommen"
        )

    st.markdown("#### Versorgungsausgleich")

    anzahl_anrechte = st.number_input(
        "Anzahl Versorgungsanrechte",
        min_value=0,
        value=2,
        step=1,
        help="Typisch: 2 (je Ehegatte ein Rentenanrecht)"
    )

    st.markdown("#### Folgesachen (optional)")

    col1, col2 = st.columns(2)

    with col1:
        mit_zugewinn = st.checkbox("Zugewinnausgleich")
        zugewinn_betrag = 0.0
        if mit_zugewinn:
            zugewinn_betrag = st.number_input(
                "Streitwert Zugewinnausgleich",
                min_value=0.0,
                value=50000.0,
                step=5000.0
            )

    with col2:
        mit_unterhalt = st.checkbox("Unterhalt")
        unterhalt_monat = 0.0
        if mit_unterhalt:
            unterhalt_monat = st.number_input(
                "Monatlicher Unterhalt",
                min_value=0.0,
                value=500.0,
                step=50.0
            )

    if st.button("Gebühren berechnen", type="primary"):
        rechner = RVGRechner()
        ergebnis = rechner.berechne_scheidungsverfahren(
            nettoeinkommen_a=netto_a,
            nettoeinkommen_b=netto_b,
            anzahl_versorgungsanrechte=anzahl_anrechte,
            mit_zugewinn=mit_zugewinn,
            zugewinn_betrag=zugewinn_betrag,
            mit_unterhalt=mit_unterhalt,
            unterhalt_monatlich=unterhalt_monat
        )
        zeige_ergebnis(ergebnis)


def render_aussergericht():
    """Rendert das Formular für außergerichtliche Vertretung"""
    st.subheader("Außergerichtliche Vertretung")

    gegenstandswert = st.number_input(
        "Gegenstandswert",
        min_value=0.0,
        value=10000.0,
        step=500.0,
        help="Wert der Angelegenheit"
    )

    col1, col2 = st.columns(2)

    with col1:
        geschaeftsgebuehr_satz = st.number_input(
            "Geschäftsgebühr (Satz)",
            min_value=0.3,
            max_value=2.5,
            value=1.3,
            step=0.1,
            help="Standard: 1,3 (Nr. 2300 VV RVG)"
        )

    with col2:
        mit_einigung = st.checkbox(
            "Mit Einigung",
            help="Zusätzlich 1,5 Einigungsgebühr"
        )

    if st.button("Gebühren berechnen", type="primary"):
        rechner = RVGRechner()
        ergebnis = rechner.berechne_aussergericht(
            gegenstandswert=gegenstandswert,
            geschaeftsgebuehr_satz=geschaeftsgebuehr_satz,
            mit_einigung=mit_einigung
        )
        zeige_ergebnis(ergebnis)


def render_gerichtlich():
    """Rendert das Formular für gerichtliche Vertretung"""
    st.subheader("Gerichtliche Vertretung")

    gegenstandswert = st.number_input(
        "Gegenstandswert",
        min_value=0.0,
        value=10000.0,
        step=500.0,
        help="Streitwert"
    )

    col1, col2 = st.columns(2)

    with col1:
        verfahrensgebuehr_satz = st.number_input(
            "Verfahrensgebühr (Satz)",
            min_value=0.3,
            max_value=2.5,
            value=1.3,
            step=0.1,
            help="Standard: 1,3 (Nr. 3100 VV RVG)"
        )

        mit_termin = st.checkbox(
            "Mit Termin",
            value=True,
            help="Terminsgebühr hinzufügen"
        )

    with col2:
        terminsgebuehr_satz = st.number_input(
            "Terminsgebühr (Satz)",
            min_value=0.3,
            max_value=2.0,
            value=1.2,
            step=0.1,
            help="Standard: 1,2 (Nr. 3104 VV RVG)",
            disabled=not mit_termin
        )

        mit_einigung = st.checkbox(
            "Mit Einigung",
            help="1,0 Einigungsgebühr bei Gericht"
        )

    if st.button("Gebühren berechnen", type="primary"):
        rechner = RVGRechner()
        ergebnis = rechner.berechne_gerichtlich(
            gegenstandswert=gegenstandswert,
            mit_termin=mit_termin,
            mit_einigung=mit_einigung,
            verfahrensgebuehr_satz=verfahrensgebuehr_satz,
            terminsgebuehr_satz=terminsgebuehr_satz if mit_termin else 1.2
        )
        zeige_ergebnis(ergebnis)


def render_erstberatung():
    """Rendert das Formular für Erstberatung"""
    st.subheader("Erstberatung")

    ist_verbraucher = st.radio(
        "Mandant ist",
        ["Verbraucher", "Unternehmer"],
        horizontal=True
    ) == "Verbraucher"

    st.info(
        "Erstberatung für Verbraucher: max. 190,00 € (§ 34 Abs. 1 S. 3 RVG)"
        if ist_verbraucher
        else "Beratung nach Vereinbarung"
    )

    if st.button("Gebühren berechnen", type="primary"):
        rechner = RVGRechner()
        ergebnis = rechner.berechne_erstberatung(ist_verbraucher)
        zeige_ergebnis(ergebnis)


def zeige_ergebnis(ergebnis: RVGErgebnis):
    """Zeigt das Berechnungsergebnis an"""
    st.markdown("---")
    st.markdown("### Gebührenberechnung")

    # Gegenstandswert
    if ergebnis.gegenstandswert > 0:
        st.markdown(f"**Gegenstandswert:** {ergebnis.gegenstandswert:,.2f} €")
        st.markdown("---")

    # Gebührenpositionen
    st.markdown("#### Gebührenpositionen")

    for pos in ergebnis.positionen:
        col1, col2 = st.columns([3, 1])

        with col1:
            if pos.gebuerensatz > 0:
                st.markdown(
                    f"**{pos.bezeichnung}** "
                    f"({pos.gebuerensatz:.1f} × {pos.einfache_gebuehr:,.2f} €)"
                )
            else:
                st.markdown(f"**{pos.bezeichnung}**")
            if pos.rechtsgrundlage:
                st.markdown(f"*{pos.rechtsgrundlage}*")

        with col2:
            st.markdown(f"**{pos.gebuehr:,.2f} €**")

    st.markdown("---")

    # Summen
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("Zwischensumme Gebühren")
    with col2:
        st.markdown(f"{ergebnis.summe_gebuehren:,.2f} €")

    if ergebnis.auslagenpauschale > 0:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Auslagenpauschale (Nr. 7002 VV RVG)")
        with col2:
            st.markdown(f"{ergebnis.auslagenpauschale:,.2f} €")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("Nettobetrag")
    with col2:
        netto = ergebnis.summe_gebuehren + ergebnis.auslagenpauschale
        st.markdown(f"{netto:,.2f} €")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("MwSt. 19%")
    with col2:
        st.markdown(f"{ergebnis.mehrwertsteuer:,.2f} €")

    st.markdown("---")

    # Gesamtbetrag
    st.success(f"**Gesamtbetrag: {ergebnis.gesamtbetrag:,.2f} €**")

    # Hinweise
    if ergebnis.hinweise:
        st.markdown("---")
        st.markdown("#### Hinweise")
        for hinweis in ergebnis.hinweise:
            st.info(hinweis)

    # Details
    if ergebnis.berechnungsdetails:
        with st.expander("Berechnungsdetails"):
            for key, value in ergebnis.berechnungsdetails.items():
                if isinstance(value, float):
                    st.markdown(f"- {key}: {value:,.2f} €")
                else:
                    st.markdown(f"- {key}: {value}")
