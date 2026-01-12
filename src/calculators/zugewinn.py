"""
Zugewinnausgleich-Berechnung nach §§ 1373 ff. BGB

Implementiert:
- Berechnung des Zugewinns je Ehegatte
- Indexierung des Anfangsvermögens (VPI)
- Berücksichtigung privilegierter Erwerbe
- Ausgleichsanspruch
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict, Any

from config.constants import VPI_REFERENZWERTE


@dataclass
class Vermoegensgegenstand:
    """Datenklasse für einen Vermögensgegenstand"""
    bezeichnung: str
    wert: float
    stichtag: date
    kategorie: str = "sonstig"  # immobilie, fahrzeug, konto, wertpapier, sonstig
    kommentar: str = ""


@dataclass
class PrivilegierterErwerb:
    """
    Datenklasse für privilegierte Erwerbe nach § 1374 Abs. 2 BGB

    - Erbschaften
    - Schenkungen mit Rücksicht auf künftiges Erbrecht
    - Ausstattungen
    """
    bezeichnung: str
    wert: float
    erwerbsdatum: date
    erwerbsart: str  # erbschaft, schenkung, ausstattung
    kommentar: str = ""


@dataclass
class EhegattenVermoegen:
    """Vermögenssituation eines Ehegatten"""
    name: str

    # Anfangsvermögen zum Heiratsdatum
    anfangsvermoegen: List[Vermoegensgegenstand] = field(default_factory=list)
    anfangsverbindlichkeiten: float = 0.0

    # Endvermögen zum Stichtag (Zustellung Scheidungsantrag)
    endvermoegen: List[Vermoegensgegenstand] = field(default_factory=list)
    endverbindlichkeiten: float = 0.0

    # Privilegierte Erwerbe (werden dem Anfangsvermögen zugerechnet)
    privilegierte_erwerbe: List[PrivilegierterErwerb] = field(default_factory=list)

    def summe_anfangsvermoegen(self) -> float:
        """Summe des Anfangsvermögens (aktiv)"""
        return sum(v.wert for v in self.anfangsvermoegen)

    def summe_endvermoegen(self) -> float:
        """Summe des Endvermögens (aktiv)"""
        return sum(v.wert for v in self.endvermoegen)

    def summe_privilegierte_erwerbe(self) -> float:
        """Summe der privilegierten Erwerbe"""
        return sum(pe.wert for pe in self.privilegierte_erwerbe)

    def netto_anfangsvermoegen(self) -> float:
        """Netto-Anfangsvermögen (Aktiva - Passiva)"""
        return self.summe_anfangsvermoegen() - self.anfangsverbindlichkeiten

    def netto_endvermoegen(self) -> float:
        """Netto-Endvermögen (Aktiva - Passiva)"""
        return self.summe_endvermoegen() - self.endverbindlichkeiten


@dataclass
class ZugewinnErgebnis:
    """Ergebnis der Zugewinnausgleichsberechnung"""
    ehegatte_a: str
    ehegatte_b: str

    # Vermögenswerte
    anfangsvermoegen_a: float
    anfangsvermoegen_b: float
    anfangsvermoegen_a_indexiert: float
    anfangsvermoegen_b_indexiert: float
    privilegierte_erwerbe_a: float
    privilegierte_erwerbe_b: float
    endvermoegen_a: float
    endvermoegen_b: float

    # Zugewinn
    zugewinn_a: float
    zugewinn_b: float
    differenz: float
    ausgleichsanspruch: float

    # Anspruchsberechtigter
    ausgleichsberechtigt: str
    ausgleichsverpflichtet: str

    # Indexierung
    vpi_heirat: float
    vpi_endstichtag: float
    indexierungsfaktor: float

    # Stichtage
    heiratsdatum: date
    endstichtag: date

    hinweise: List[str] = field(default_factory=list)
    berechnungsdetails: Dict[str, Any] = field(default_factory=dict)


class ZugewinnausgleichRechner:
    """
    Rechner für den Zugewinnausgleich nach §§ 1373 ff. BGB

    Grundprinzip:
    Der Zugewinn ist der Betrag, um den das Endvermögen eines Ehegatten
    sein Anfangsvermögen übersteigt. Der Ehegatte mit dem geringeren
    Zugewinn hat Anspruch auf die Hälfte der Differenz.
    """

    def __init__(self, vpi_tabelle: Dict[int, float] = None):
        self.vpi_tabelle = vpi_tabelle or VPI_REFERENZWERTE

    def hole_vpi(self, datum: date) -> float:
        """
        Holt den VPI-Wert für ein bestimmtes Datum

        Verwendet den Jahreswert. Bei fehlendem Jahr wird interpoliert
        oder der nächstliegende Wert verwendet.
        """
        jahr = datum.year

        if jahr in self.vpi_tabelle:
            return self.vpi_tabelle[jahr]

        # Interpolation oder nächster Wert
        jahre = sorted(self.vpi_tabelle.keys())

        if jahr < jahre[0]:
            return self.vpi_tabelle[jahre[0]]

        if jahr > jahre[-1]:
            return self.vpi_tabelle[jahre[-1]]

        # Lineare Interpolation
        for i, j in enumerate(jahre[:-1]):
            if j < jahr < jahre[i + 1]:
                vpi_unten = self.vpi_tabelle[j]
                vpi_oben = self.vpi_tabelle[jahre[i + 1]]
                anteil = (jahr - j) / (jahre[i + 1] - j)
                return vpi_unten + (vpi_oben - vpi_unten) * anteil

        return 100.0  # Fallback

    def indexiere_anfangsvermoegen(
        self,
        anfangsvermoegen: float,
        heiratsdatum: date,
        endstichtag: date
    ) -> tuple[float, float, float]:
        """
        Indexiert das Anfangsvermögen auf den Endstichtag

        Formel: Indexiert = Anfangsvermögen × (VPI_End / VPI_Heirat)

        Returns:
            Tuple aus (indexiertes_vermoegen, vpi_heirat, vpi_end)
        """
        vpi_heirat = self.hole_vpi(heiratsdatum)
        vpi_end = self.hole_vpi(endstichtag)

        if vpi_heirat == 0:
            vpi_heirat = 100.0  # Sicherheit

        indexierungsfaktor = vpi_end / vpi_heirat
        indexiert = anfangsvermoegen * indexierungsfaktor

        return indexiert, vpi_heirat, vpi_end

    def berechne_zugewinn(
        self,
        endvermoegen: float,
        anfangsvermoegen_indexiert: float,
        privilegierte_erwerbe: float
    ) -> float:
        """
        Berechnet den Zugewinn eines Ehegatten

        Formel: Zugewinn = Endvermögen - Anfangsvermögen (indexiert) - Privilegierte Erwerbe

        Der Zugewinn kann nicht negativ sein (§ 1373 BGB).
        """
        zugewinn = endvermoegen - anfangsvermoegen_indexiert - privilegierte_erwerbe
        return max(0.0, zugewinn)

    def berechne_ausgleich(
        self,
        zugewinn_a: float,
        zugewinn_b: float
    ) -> tuple[float, str, str]:
        """
        Berechnet den Ausgleichsanspruch

        Formel: Ausgleich = (Höherer Zugewinn - Niedrigerer Zugewinn) / 2

        Returns:
            Tuple aus (ausgleichsanspruch, name_berechtigt, name_verpflichtet)
        """
        differenz = abs(zugewinn_a - zugewinn_b)
        ausgleich = differenz / 2

        if zugewinn_a > zugewinn_b:
            return ausgleich, "Ehegatte B", "Ehegatte A"
        elif zugewinn_b > zugewinn_a:
            return ausgleich, "Ehegatte A", "Ehegatte B"
        else:
            return 0.0, "", ""

    def berechne(
        self,
        ehegatte_a: EhegattenVermoegen,
        ehegatte_b: EhegattenVermoegen,
        heiratsdatum: date,
        endstichtag: date
    ) -> ZugewinnErgebnis:
        """
        Hauptmethode zur Berechnung des Zugewinnausgleichs

        Args:
            ehegatte_a: Vermögenssituation Ehegatte A
            ehegatte_b: Vermögenssituation Ehegatte B
            heiratsdatum: Datum der standesamtlichen Eheschließung
            endstichtag: Datum der Zustellung des Scheidungsantrags

        Returns:
            ZugewinnErgebnis mit vollständiger Berechnung
        """
        hinweise = []

        # 1. Anfangsvermögen berechnen
        anfang_a = ehegatte_a.netto_anfangsvermoegen()
        anfang_b = ehegatte_b.netto_anfangsvermoegen()

        # 2. Anfangsvermögen indexieren
        anfang_a_idx, vpi_heirat, vpi_end = self.indexiere_anfangsvermoegen(
            anfang_a, heiratsdatum, endstichtag
        )
        anfang_b_idx, _, _ = self.indexiere_anfangsvermoegen(
            anfang_b, heiratsdatum, endstichtag
        )

        indexierungsfaktor = vpi_end / vpi_heirat if vpi_heirat > 0 else 1.0

        # 3. Privilegierte Erwerbe
        priv_a = ehegatte_a.summe_privilegierte_erwerbe()
        priv_b = ehegatte_b.summe_privilegierte_erwerbe()

        # Privilegierte Erwerbe auch indexieren (auf jeweiliges Erwerbsdatum)
        # Vereinfachung: Hier werden sie zum Nennwert angesetzt
        if priv_a > 0:
            hinweise.append(
                f"{ehegatte_a.name}: Privilegierte Erwerbe i.H.v. {priv_a:,.2f}€ "
                "(Erbschaften/Schenkungen) werden dem Anfangsvermögen hinzugerechnet."
            )
        if priv_b > 0:
            hinweise.append(
                f"{ehegatte_b.name}: Privilegierte Erwerbe i.H.v. {priv_b:,.2f}€ "
                "(Erbschaften/Schenkungen) werden dem Anfangsvermögen hinzugerechnet."
            )

        # 4. Endvermögen berechnen
        end_a = ehegatte_a.netto_endvermoegen()
        end_b = ehegatte_b.netto_endvermoegen()

        # 5. Zugewinn berechnen
        zugewinn_a = self.berechne_zugewinn(end_a, anfang_a_idx, priv_a)
        zugewinn_b = self.berechne_zugewinn(end_b, anfang_b_idx, priv_b)

        # Hinweis bei negativem Vermögenszuwachs
        if end_a < anfang_a_idx + priv_a:
            hinweise.append(
                f"{ehegatte_a.name}: Kein Zugewinn (Endvermögen geringer als "
                "indexiertes Anfangsvermögen + privilegierte Erwerbe)."
            )
        if end_b < anfang_b_idx + priv_b:
            hinweise.append(
                f"{ehegatte_b.name}: Kein Zugewinn (Endvermögen geringer als "
                "indexiertes Anfangsvermögen + privilegierte Erwerbe)."
            )

        # 6. Ausgleich berechnen
        differenz = abs(zugewinn_a - zugewinn_b)
        ausgleich = differenz / 2

        if zugewinn_a > zugewinn_b:
            berechtigt = ehegatte_b.name
            verpflichtet = ehegatte_a.name
        elif zugewinn_b > zugewinn_a:
            berechtigt = ehegatte_a.name
            verpflichtet = ehegatte_b.name
        else:
            berechtigt = ""
            verpflichtet = ""
            hinweise.append("Beide Ehegatten haben den gleichen Zugewinn. Kein Ausgleich erforderlich.")

        # 7. Berechnungsdetails
        berechnungsdetails = {
            "ehedauer_jahre": (endstichtag - heiratsdatum).days / 365.25,
            "inflation_prozent": (indexierungsfaktor - 1) * 100,
            "aktiva_a": ehegatte_a.summe_anfangsvermoegen(),
            "aktiva_b": ehegatte_b.summe_anfangsvermoegen(),
            "passiva_a": ehegatte_a.anfangsverbindlichkeiten,
            "passiva_b": ehegatte_b.anfangsverbindlichkeiten,
            "endaktiva_a": ehegatte_a.summe_endvermoegen(),
            "endaktiva_b": ehegatte_b.summe_endvermoegen(),
            "endpassiva_a": ehegatte_a.endverbindlichkeiten,
            "endpassiva_b": ehegatte_b.endverbindlichkeiten,
        }

        return ZugewinnErgebnis(
            ehegatte_a=ehegatte_a.name,
            ehegatte_b=ehegatte_b.name,
            anfangsvermoegen_a=anfang_a,
            anfangsvermoegen_b=anfang_b,
            anfangsvermoegen_a_indexiert=anfang_a_idx,
            anfangsvermoegen_b_indexiert=anfang_b_idx,
            privilegierte_erwerbe_a=priv_a,
            privilegierte_erwerbe_b=priv_b,
            endvermoegen_a=end_a,
            endvermoegen_b=end_b,
            zugewinn_a=zugewinn_a,
            zugewinn_b=zugewinn_b,
            differenz=differenz,
            ausgleichsanspruch=ausgleich,
            ausgleichsberechtigt=berechtigt,
            ausgleichsverpflichtet=verpflichtet,
            vpi_heirat=vpi_heirat,
            vpi_endstichtag=vpi_end,
            indexierungsfaktor=indexierungsfaktor,
            heiratsdatum=heiratsdatum,
            endstichtag=endstichtag,
            hinweise=hinweise,
            berechnungsdetails=berechnungsdetails
        )

    def formatiere_ergebnis(self, ergebnis: ZugewinnErgebnis) -> str:
        """Formatiert das Ergebnis als lesbaren Text"""
        lines = [
            "=" * 70,
            "ZUGEWINNAUSGLEICH (§§ 1373 ff. BGB)",
            "=" * 70,
            "",
            f"Heiratsdatum:   {ergebnis.heiratsdatum.strftime('%d.%m.%Y')}",
            f"Endstichtag:    {ergebnis.endstichtag.strftime('%d.%m.%Y')}",
            f"Ehedauer:       {ergebnis.berechnungsdetails.get('ehedauer_jahre', 0):.1f} Jahre",
            "",
            f"VPI Heirat:     {ergebnis.vpi_heirat:.1f}",
            f"VPI Endstichtag:{ergebnis.vpi_endstichtag:.1f}",
            f"Indexierung:    {ergebnis.indexierungsfaktor:.4f} "
            f"(+{ergebnis.berechnungsdetails.get('inflation_prozent', 0):.1f}%)",
            "",
            "-" * 70,
            f"{'':30} {ergebnis.ehegatte_a:>18} {ergebnis.ehegatte_b:>18}",
            "-" * 70,
            "",
            "ANFANGSVERMÖGEN:",
            f"{'  Netto (Nominalwert):':30} {ergebnis.anfangsvermoegen_a:>15,.2f}€ "
            f"{ergebnis.anfangsvermoegen_b:>15,.2f}€",
            f"{'  Indexiert:':30} {ergebnis.anfangsvermoegen_a_indexiert:>15,.2f}€ "
            f"{ergebnis.anfangsvermoegen_b_indexiert:>15,.2f}€",
            f"{'  + Privilegierte Erwerbe:':30} {ergebnis.privilegierte_erwerbe_a:>15,.2f}€ "
            f"{ergebnis.privilegierte_erwerbe_b:>15,.2f}€",
            "",
            "ENDVERMÖGEN:",
            f"{'  Netto:':30} {ergebnis.endvermoegen_a:>15,.2f}€ "
            f"{ergebnis.endvermoegen_b:>15,.2f}€",
            "",
            "-" * 70,
            f"{'ZUGEWINN:':30} {ergebnis.zugewinn_a:>15,.2f}€ "
            f"{ergebnis.zugewinn_b:>15,.2f}€",
            "-" * 70,
            "",
            f"Differenz der Zugewinne: {ergebnis.differenz:>15,.2f}€",
            f"Ausgleichsanspruch (50%): {ergebnis.ausgleichsanspruch:>14,.2f}€",
            "",
        ]

        if ergebnis.ausgleichsberechtigt:
            lines.extend([
                "-" * 70,
                f"ERGEBNIS: {ergebnis.ausgleichsverpflichtet} schuldet",
                f"          {ergebnis.ausgleichsberechtigt} einen Ausgleich von",
                f"          {ergebnis.ausgleichsanspruch:,.2f}€",
                "-" * 70,
            ])

        if ergebnis.hinweise:
            lines.extend([
                "",
                "HINWEISE:",
            ])
            for hinweis in ergebnis.hinweise:
                lines.append(f"  • {hinweis}")

        lines.append("=" * 70)

        return "\n".join(lines)
