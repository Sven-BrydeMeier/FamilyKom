"""
Ehegattenunterhalt-Berechnung

Implementiert:
- Trennungsunterhalt (§ 1361 BGB)
- Nachehelicher Unterhalt (§§ 1569 ff. BGB)
- OLG-Leitlinien Schleswig-Holstein 2025
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional, Dict, Any

from config.constants import (
    SELBSTBEHALT_2025,
    SelbstbehaltTyp,
    NachehelicheUnterhaltstatbestaende,
    OLG_SCHLESWIG_LEITLINIEN_2025,
)


class Unterhaltstyp(Enum):
    """Art des Ehegattenunterhalts"""
    TRENNUNGSUNTERHALT = "trennungsunterhalt"
    NACHEHELICHER_UNTERHALT = "nachehelicher_unterhalt"


@dataclass
class Ehegatte:
    """Datenklasse für einen Ehegatten"""
    name: str
    erwerbstaetig: bool
    bruttoeinkommen: float
    nettoeinkommen: float
    berufsbedingte_aufwendungen: Optional[float] = None
    sonstige_einkuenfte: float = 0.0  # z.B. Mieteinnahmen, Kapitalerträge
    wohnvorteil: float = 0.0  # Mietwert eigener Immobilie abzgl. Belastungen
    kindesunterhalt_zahlbetrag: float = 0.0  # Vorrangiger Kindesunterhalt

    def berechne_bereinigte_aufwendungen(self) -> float:
        """Berechnet berufsbedingte Aufwendungen nach OLG-Leitlinien"""
        if not self.erwerbstaetig:
            return 0.0

        if self.berufsbedingte_aufwendungen is not None:
            return self.berufsbedingte_aufwendungen

        pauschal = self.nettoeinkommen * OLG_SCHLESWIG_LEITLINIEN_2025["berufsbedingte_aufwendungen_pauschal"]
        return max(
            OLG_SCHLESWIG_LEITLINIEN_2025["berufsbedingte_aufwendungen_min"],
            min(pauschal, OLG_SCHLESWIG_LEITLINIEN_2025["berufsbedingte_aufwendungen_max"])
        )

    def berechne_bereinigtes_erwerbseinkommen(self) -> float:
        """Berechnet das bereinigte Erwerbseinkommen"""
        if not self.erwerbstaetig:
            return 0.0

        bereinigt = self.nettoeinkommen
        bereinigt -= self.berechne_bereinigte_aufwendungen()
        bereinigt -= self.kindesunterhalt_zahlbetrag
        return max(0, bereinigt)

    def berechne_gesamteinkommen(self) -> float:
        """Berechnet das Gesamteinkommen inkl. sonstiger Einkünfte"""
        erwerbseinkommen = self.berechne_bereinigtes_erwerbseinkommen()
        return erwerbseinkommen + self.sonstige_einkuenfte + self.wohnvorteil


@dataclass
class UnterhaltsTatbestand:
    """Datenklasse für einen Unterhaltstatbestand"""
    paragraph: str
    bezeichnung: str
    erfuellt: bool = False
    begruendung: str = ""


@dataclass
class EhegattenunterhaltErgebnis:
    """Ergebnis der Ehegattenunterhalt-Berechnung"""
    unterhaltstyp: Unterhaltstyp
    pflichtiger: str
    berechtigter: str

    einkommen_pflichtiger: float
    einkommen_berechtigter: float
    differenz: float

    quote: float  # 0.45 oder 0.50
    erwerbstaetigenbonus: float

    unterhalt_vor_selbstbehalt: float
    unterhalt_nach_selbstbehalt: float
    selbstbehalt: float
    selbstbehalt_unterschritten: bool

    tatbestaende: List[UnterhaltsTatbestand] = field(default_factory=list)
    hinweise: List[str] = field(default_factory=list)
    berechnungsdetails: Dict[str, Any] = field(default_factory=dict)


class EhegattenunterhaltRechner:
    """
    Rechner für Ehegattenunterhalt

    Berechnungsmethoden:
    - Differenzmethode (Standard)
    - Additionsmethode (bei beiderseitigem Erwerbseinkommen)

    Berücksichtigt:
    - Erwerbstätigenbonus (1/10 OLG Schleswig-Holstein)
    - Vorrangigen Kindesunterhalt
    - Selbstbehalt
    """

    def __init__(self):
        self.leitlinien = OLG_SCHLESWIG_LEITLINIEN_2025

    def berechne_trennungsunterhalt(
        self,
        pflichtiger: Ehegatte,
        berechtigter: Ehegatte
    ) -> EhegattenunterhaltErgebnis:
        """
        Berechnet den Trennungsunterhalt nach § 1361 BGB

        Formel bei erwerbstätigem Pflichtigen:
        - Berechtigter ohne Einkommen: 45% des bereinigten Nettoeinkommens
        - Berechtigter mit Einkommen: 45% der Einkommensdifferenz

        Bei nicht erwerbstätigem Pflichtigen: 50% statt 45%
        """
        # Einkommen ermitteln
        einkommen_p = pflichtiger.berechne_gesamteinkommen()
        einkommen_b = berechtigter.berechne_gesamteinkommen()

        # Erwerbstätigenbonus berechnen (1/10 des Erwerbseinkommens)
        bonus_p = 0.0
        bonus_b = 0.0

        if pflichtiger.erwerbstaetig:
            bonus_p = pflichtiger.berechne_bereinigtes_erwerbseinkommen() * self.leitlinien["erwerbstaetigenbonus"]

        if berechtigter.erwerbstaetig:
            bonus_b = berechtigter.berechne_bereinigtes_erwerbseinkommen() * self.leitlinien["erwerbstaetigenbonus"]

        # Für die Unterhaltsberechnung relevante Einkommen (nach Bonusabzug)
        relevantes_einkommen_p = einkommen_p - bonus_p
        relevantes_einkommen_b = einkommen_b - bonus_b

        # Differenz berechnen
        differenz = relevantes_einkommen_p - relevantes_einkommen_b

        # Quote bestimmen (45% bei Erwerbstätigkeit, 50% sonst)
        if pflichtiger.erwerbstaetig:
            quote = 0.45
        else:
            quote = 0.50

        # Unterhalt berechnen
        if differenz > 0:
            unterhalt = differenz * quote
        else:
            unterhalt = 0.0

        # Selbstbehalt prüfen
        if pflichtiger.erwerbstaetig:
            selbstbehalt = float(SELBSTBEHALT_2025[SelbstbehaltTyp.EHEGATTE_ERWERBSTAETIG])
        else:
            selbstbehalt = float(SELBSTBEHALT_2025[SelbstbehaltTyp.EHEGATTE_NICHT_ERWERBSTAETIG])

        verbleibendes_einkommen = einkommen_p - unterhalt
        selbstbehalt_unterschritten = verbleibendes_einkommen < selbstbehalt

        unterhalt_nach_selbstbehalt = unterhalt
        if selbstbehalt_unterschritten:
            unterhalt_nach_selbstbehalt = max(0, einkommen_p - selbstbehalt)

        # Hinweise sammeln
        hinweise = []
        if selbstbehalt_unterschritten:
            hinweise.append(
                f"Selbstbehalt unterschritten: Unterhalt von {unterhalt:.2f}€ "
                f"auf {unterhalt_nach_selbstbehalt:.2f}€ reduziert"
            )

        if pflichtiger.kindesunterhalt_zahlbetrag > 0:
            hinweise.append(
                f"Vorrangiger Kindesunterhalt i.H.v. {pflichtiger.kindesunterhalt_zahlbetrag:.2f}€ "
                "wurde bereits vom Einkommen abgezogen"
            )

        return EhegattenunterhaltErgebnis(
            unterhaltstyp=Unterhaltstyp.TRENNUNGSUNTERHALT,
            pflichtiger=pflichtiger.name,
            berechtigter=berechtigter.name,
            einkommen_pflichtiger=einkommen_p,
            einkommen_berechtigter=einkommen_b,
            differenz=differenz,
            quote=quote,
            erwerbstaetigenbonus=bonus_p + bonus_b,
            unterhalt_vor_selbstbehalt=unterhalt,
            unterhalt_nach_selbstbehalt=unterhalt_nach_selbstbehalt,
            selbstbehalt=selbstbehalt,
            selbstbehalt_unterschritten=selbstbehalt_unterschritten,
            hinweise=hinweise,
            berechnungsdetails={
                "erwerbseinkommen_pflichtiger": pflichtiger.berechne_bereinigtes_erwerbseinkommen(),
                "erwerbseinkommen_berechtigter": berechtigter.berechne_bereinigtes_erwerbseinkommen(),
                "sonstige_einkuenfte_pflichtiger": pflichtiger.sonstige_einkuenfte,
                "sonstige_einkuenfte_berechtigter": berechtigter.sonstige_einkuenfte,
                "wohnvorteil_pflichtiger": pflichtiger.wohnvorteil,
                "wohnvorteil_berechtigter": berechtigter.wohnvorteil,
                "bonus_pflichtiger": bonus_p,
                "bonus_berechtigter": bonus_b,
            }
        )

    def pruefe_unterhalts_tatbestaende(
        self,
        berechtigter: Ehegatte,
        kinder_unter_3: bool = False,
        alter_bei_scheidung: Optional[int] = None,
        krankheit_gebrechen: bool = False,
        keine_angemessene_arbeit: bool = False,
        ausbildung_fortbildung: bool = False,
        billigkeitsgruende: str = ""
    ) -> List[UnterhaltsTatbestand]:
        """
        Prüft die Unterhaltstatbestände nach §§ 1570 ff. BGB

        Returns:
            Liste der geprüften Tatbestände mit Erfüllungsstatus
        """
        tatbestaende = []

        # § 1570 BGB - Betreuungsunterhalt
        tb_betreuung = UnterhaltsTatbestand(
            paragraph="§ 1570 BGB",
            bezeichnung="Betreuungsunterhalt",
            erfuellt=kinder_unter_3,
            begruendung="Betreuung eines Kindes unter 3 Jahren" if kinder_unter_3 else ""
        )
        tatbestaende.append(tb_betreuung)

        # § 1571 BGB - Altersunterhalt
        tb_alter = UnterhaltsTatbestand(
            paragraph="§ 1571 BGB",
            bezeichnung="Altersunterhalt",
            erfuellt=alter_bei_scheidung is not None and alter_bei_scheidung >= 65,
            begruendung=f"Alter bei Scheidung: {alter_bei_scheidung} Jahre" if alter_bei_scheidung else ""
        )
        tatbestaende.append(tb_alter)

        # § 1572 BGB - Krankheitsunterhalt
        tb_krankheit = UnterhaltsTatbestand(
            paragraph="§ 1572 BGB",
            bezeichnung="Krankheitsunterhalt",
            erfuellt=krankheit_gebrechen,
            begruendung="Krankheit oder Gebrechen liegt vor" if krankheit_gebrechen else ""
        )
        tatbestaende.append(tb_krankheit)

        # § 1573 Abs. 1 BGB - Erwerbslosigkeitsunterhalt
        tb_erwerbslos = UnterhaltsTatbestand(
            paragraph="§ 1573 Abs. 1 BGB",
            bezeichnung="Erwerbslosigkeitsunterhalt",
            erfuellt=keine_angemessene_arbeit and not berechtigter.erwerbstaetig,
            begruendung="Keine angemessene Erwerbstätigkeit möglich" if keine_angemessene_arbeit else ""
        )
        tatbestaende.append(tb_erwerbslos)

        # § 1573 Abs. 2 BGB - Aufstockungsunterhalt
        # Wird separat berechnet wenn Einkommen nicht ausreicht
        tb_aufstockung = UnterhaltsTatbestand(
            paragraph="§ 1573 Abs. 2 BGB",
            bezeichnung="Aufstockungsunterhalt",
            erfuellt=berechtigter.erwerbstaetig,  # Grundsätzlich prüfbar wenn erwerbstätig
            begruendung="Eigenes Einkommen reicht nicht für angemessenen Lebensstandard"
            if berechtigter.erwerbstaetig else ""
        )
        tatbestaende.append(tb_aufstockung)

        # § 1574 BGB - Ausbildungsunterhalt
        tb_ausbildung = UnterhaltsTatbestand(
            paragraph="§ 1574 BGB",
            bezeichnung="Ausbildungsunterhalt",
            erfuellt=ausbildung_fortbildung,
            begruendung="Ausbildung oder Fortbildung wird absolviert" if ausbildung_fortbildung else ""
        )
        tatbestaende.append(tb_ausbildung)

        # § 1576 BGB - Billigkeitsunterhalt
        tb_billigkeit = UnterhaltsTatbestand(
            paragraph="§ 1576 BGB",
            bezeichnung="Billigkeitsunterhalt",
            erfuellt=bool(billigkeitsgruende),
            begruendung=billigkeitsgruende
        )
        tatbestaende.append(tb_billigkeit)

        return tatbestaende

    def berechne_nachehelichen_unterhalt(
        self,
        pflichtiger: Ehegatte,
        berechtigter: Ehegatte,
        tatbestaende: List[UnterhaltsTatbestand]
    ) -> EhegattenunterhaltErgebnis:
        """
        Berechnet den nachehelichen Unterhalt nach §§ 1569 ff. BGB

        Voraussetzung: Mindestens ein Unterhaltstatbestand muss erfüllt sein
        """
        # Prüfen ob mindestens ein Tatbestand erfüllt ist
        erfuellte_tatbestaende = [tb for tb in tatbestaende if tb.erfuellt]

        hinweise = []

        if not erfuellte_tatbestaende:
            hinweise.append(
                "Kein Unterhaltstatbestand nach §§ 1570-1576 BGB erfüllt. "
                "Grundsatz der Eigenverantwortung gilt (§ 1569 BGB)."
            )

        # Berechnung analog zum Trennungsunterhalt
        einkommen_p = pflichtiger.berechne_gesamteinkommen()
        einkommen_b = berechtigter.berechne_gesamteinkommen()

        # Erwerbstätigenbonus
        bonus_p = 0.0
        bonus_b = 0.0

        if pflichtiger.erwerbstaetig:
            bonus_p = pflichtiger.berechne_bereinigtes_erwerbseinkommen() * self.leitlinien["erwerbstaetigenbonus"]

        if berechtigter.erwerbstaetig:
            bonus_b = berechtigter.berechne_bereinigtes_erwerbseinkommen() * self.leitlinien["erwerbstaetigenbonus"]

        relevantes_einkommen_p = einkommen_p - bonus_p
        relevantes_einkommen_b = einkommen_b - bonus_b

        differenz = relevantes_einkommen_p - relevantes_einkommen_b

        if pflichtiger.erwerbstaetig:
            quote = 0.45
        else:
            quote = 0.50

        # Unterhalt nur wenn Tatbestand erfüllt UND Differenz positiv
        if erfuellte_tatbestaende and differenz > 0:
            unterhalt = differenz * quote
        else:
            unterhalt = 0.0

        # Selbstbehalt
        if pflichtiger.erwerbstaetig:
            selbstbehalt = float(SELBSTBEHALT_2025[SelbstbehaltTyp.EHEGATTE_ERWERBSTAETIG])
        else:
            selbstbehalt = float(SELBSTBEHALT_2025[SelbstbehaltTyp.EHEGATTE_NICHT_ERWERBSTAETIG])

        verbleibendes_einkommen = einkommen_p - unterhalt
        selbstbehalt_unterschritten = verbleibendes_einkommen < selbstbehalt

        unterhalt_nach_selbstbehalt = unterhalt
        if selbstbehalt_unterschritten:
            unterhalt_nach_selbstbehalt = max(0, einkommen_p - selbstbehalt)
            hinweise.append(
                f"Selbstbehalt unterschritten: Unterhalt auf {unterhalt_nach_selbstbehalt:.2f}€ reduziert"
            )

        # Hinweis zu erfüllten Tatbeständen
        if erfuellte_tatbestaende:
            tb_namen = ", ".join([f"{tb.paragraph} ({tb.bezeichnung})" for tb in erfuellte_tatbestaende])
            hinweise.append(f"Erfüllte Tatbestände: {tb_namen}")

        return EhegattenunterhaltErgebnis(
            unterhaltstyp=Unterhaltstyp.NACHEHELICHER_UNTERHALT,
            pflichtiger=pflichtiger.name,
            berechtigter=berechtigter.name,
            einkommen_pflichtiger=einkommen_p,
            einkommen_berechtigter=einkommen_b,
            differenz=differenz,
            quote=quote,
            erwerbstaetigenbonus=bonus_p + bonus_b,
            unterhalt_vor_selbstbehalt=unterhalt,
            unterhalt_nach_selbstbehalt=unterhalt_nach_selbstbehalt,
            selbstbehalt=selbstbehalt,
            selbstbehalt_unterschritten=selbstbehalt_unterschritten,
            tatbestaende=tatbestaende,
            hinweise=hinweise,
            berechnungsdetails={
                "erwerbseinkommen_pflichtiger": pflichtiger.berechne_bereinigtes_erwerbseinkommen(),
                "erwerbseinkommen_berechtigter": berechtigter.berechne_bereinigtes_erwerbseinkommen(),
                "sonstige_einkuenfte_pflichtiger": pflichtiger.sonstige_einkuenfte,
                "sonstige_einkuenfte_berechtigter": berechtigter.sonstige_einkuenfte,
                "anzahl_erfuellte_tatbestaende": len(erfuellte_tatbestaende),
            }
        )

    def formatiere_ergebnis(self, ergebnis: EhegattenunterhaltErgebnis) -> str:
        """Formatiert das Ergebnis als lesbaren Text"""
        typ_bezeichnung = (
            "TRENNUNGSUNTERHALT (§ 1361 BGB)"
            if ergebnis.unterhaltstyp == Unterhaltstyp.TRENNUNGSUNTERHALT
            else "NACHEHELICHER UNTERHALT (§§ 1569 ff. BGB)"
        )

        lines = [
            "=" * 60,
            typ_bezeichnung,
            "=" * 60,
            "",
            f"Unterhaltspflichtiger: {ergebnis.pflichtiger}",
            f"Unterhaltsberechtigter: {ergebnis.berechtigter}",
            "",
            "-" * 60,
            "EINKOMMENSERMITTLUNG:",
            "-" * 60,
            f"Einkommen Pflichtiger:   {ergebnis.einkommen_pflichtiger:>10,.2f} €",
            f"Einkommen Berechtigter:  {ergebnis.einkommen_berechtigter:>10,.2f} €",
            f"Differenz:               {ergebnis.differenz:>10,.2f} €",
            "",
            f"Erwerbstätigenbonus:     {ergebnis.erwerbstaetigenbonus:>10,.2f} €",
            f"Quote:                   {ergebnis.quote * 100:.0f}%",
            "",
            "-" * 60,
            "UNTERHALT:",
            "-" * 60,
            f"Unterhalt (berechnet):   {ergebnis.unterhalt_vor_selbstbehalt:>10,.2f} €",
            f"Selbstbehalt:            {ergebnis.selbstbehalt:>10,.2f} €",
            f"Unterhalt (Zahlbetrag):  {ergebnis.unterhalt_nach_selbstbehalt:>10,.2f} €",
        ]

        if ergebnis.tatbestaende:
            lines.extend([
                "",
                "-" * 60,
                "UNTERHALTSTATBESTÄNDE:",
                "-" * 60,
            ])
            for tb in ergebnis.tatbestaende:
                status = "✓" if tb.erfuellt else "✗"
                lines.append(f"  {status} {tb.paragraph}: {tb.bezeichnung}")
                if tb.begruendung:
                    lines.append(f"      {tb.begruendung}")

        if ergebnis.hinweise:
            lines.extend([
                "",
                "-" * 60,
                "HINWEISE:",
                "-" * 60,
            ])
            for hinweis in ergebnis.hinweise:
                lines.append(f"  • {hinweis}")

        lines.append("=" * 60)

        return "\n".join(lines)
