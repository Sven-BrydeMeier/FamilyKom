"""
FamilyKom Calculation Engine - RVG Gebuehren
=============================================

Berechnung der Rechtsanwaltsgebuehren nach RVG/FamGKG.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Any

from .base import (
    BerechnungsTyp, CalculationResult, CalculationStep,
    CalculationWarning, RulesetInfo
)


# RVG Gebuehrentabelle (Anlage 2 zu § 13 RVG) - Auszug
RVG_TABELLE = {
    500: 49, 1000: 88, 1500: 127, 2000: 166, 3000: 222,
    4000: 278, 5000: 334, 6000: 390, 7000: 446, 8000: 502,
    9000: 558, 10000: 614, 13000: 666, 16000: 718, 19000: 770,
    22000: 822, 25000: 874, 30000: 955, 35000: 1036, 40000: 1117,
    45000: 1198, 50000: 1279, 65000: 1373, 80000: 1467, 95000: 1561,
    110000: 1655, 125000: 1749, 140000: 1843, 155000: 1937, 170000: 2031,
    185000: 2125, 200000: 2219, 230000: 2360, 260000: 2501, 290000: 2642,
    320000: 2783, 350000: 2924, 380000: 3065, 410000: 3206, 440000: 3347,
    470000: 3488, 500000: 3629,
}


@dataclass
class RVGEingabe:
    """Eingabewerte fuer RVG-Berechnung"""
    gegenstandswert: float
    gebuehrenart: str  # 'verfahren', 'termins', 'einigung'
    faktor: float = 1.3  # Regelsatz
    mehrere_auftraggeber: int = 1
    auslagen_pauschale: bool = True
    umsatzsteuer: bool = True


class RVGCalculator:
    """Rechner fuer RVG-Gebuehren"""

    UMSATZSTEUER_SATZ = 0.19
    AUSLAGEN_PAUSCHALE = 20.0  # Nr. 7002 VV RVG

    @classmethod
    def get_wertgebuehr(cls, gegenstandswert: float) -> float:
        """Ermittelt die Wertgebuehr nach RVG-Tabelle"""
        # Sortierte Liste der Schwellenwerte
        schwellen = sorted(RVG_TABELLE.keys())

        for schwelle in schwellen:
            if gegenstandswert <= schwelle:
                return RVG_TABELLE[schwelle]

        # Ueber hoechstem Tabellenwert: Berechnung nach § 13 Abs. 2 RVG
        letzte_gebuehr = RVG_TABELLE[500000]
        ueberschuss = gegenstandswert - 500000
        zusatz = (ueberschuss // 50000) * 165
        return letzte_gebuehr + zusatz

    def berechne(self, eingabe: RVGEingabe) -> CalculationResult:
        """Fuehrt die RVG-Gebuehrenberechnung durch"""
        schritte: List[CalculationStep] = []
        warnungen: List[CalculationWarning] = []
        schritt_nr = 0

        # ===== Schritt 1: Wertgebuehr ermitteln =====
        schritt_nr += 1
        wertgebuehr = self.get_wertgebuehr(eingabe.gegenstandswert)

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Wertgebuehr nach RVG-Tabelle",
            formel="Tabellenwert fuer Gegenstandswert",
            eingabewerte={"gegenstandswert": eingabe.gegenstandswert},
            ergebnis=wertgebuehr,
            erlaeuterung=f"Gebuehr fuer {eingabe.gegenstandswert:.2f} EUR"
        ))

        # ===== Schritt 2: Gebuehr mit Faktor =====
        schritt_nr += 1
        gebuehr = wertgebuehr * eingabe.faktor

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Gebuehr mit Faktor",
            formel="Wertgebuehr x Faktor",
            eingabewerte={
                "wertgebuehr": wertgebuehr,
                "faktor": eingabe.faktor
            },
            ergebnis=round(gebuehr, 2),
            erlaeuterung=f"{eingabe.faktor}-fache Gebuehr"
        ))

        # ===== Schritt 3: Erhoehung bei mehreren Auftraggebern =====
        schritt_nr += 1
        if eingabe.mehrere_auftraggeber > 1:
            erhoehung = gebuehr * 0.3 * (eingabe.mehrere_auftraggeber - 1)
            erhoehung = min(erhoehung, gebuehr * 2)  # max 2-fache
            gebuehr += erhoehung
            erlaeuterung = f"Erhoehung um {erhoehung:.2f} EUR"
        else:
            erhoehung = 0
            erlaeuterung = "Keine Erhoehung"

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Erhoehung mehrere Auftraggeber",
            formel="+ 0,3 pro weiterem Auftraggeber (max. 2-fach)",
            eingabewerte={"auftraggeber": eingabe.mehrere_auftraggeber},
            ergebnis=round(erhoehung, 2),
            erlaeuterung=erlaeuterung
        ))

        # ===== Schritt 4: Auslagenpauschale =====
        schritt_nr += 1
        auslagen = self.AUSLAGEN_PAUSCHALE if eingabe.auslagen_pauschale else 0

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Auslagenpauschale (Nr. 7002 VV RVG)",
            formel="Pauschale 20,00 EUR",
            eingabewerte={"pauschale_aktiv": eingabe.auslagen_pauschale},
            ergebnis=auslagen,
            erlaeuterung="Post-/Telekommunikationspauschale"
        ))

        # ===== Schritt 5: Zwischensumme =====
        schritt_nr += 1
        zwischensumme = gebuehr + auslagen

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Zwischensumme netto",
            formel="Gebuehr + Auslagen",
            eingabewerte={
                "gebuehr": gebuehr,
                "auslagen": auslagen
            },
            ergebnis=round(zwischensumme, 2),
            erlaeuterung=None
        ))

        # ===== Schritt 6: Umsatzsteuer =====
        schritt_nr += 1
        if eingabe.umsatzsteuer:
            ust = zwischensumme * self.UMSATZSTEUER_SATZ
        else:
            ust = 0

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Umsatzsteuer (19%)",
            formel="Zwischensumme x 0,19",
            eingabewerte={"ust_pflichtig": eingabe.umsatzsteuer},
            ergebnis=round(ust, 2),
            erlaeuterung=None
        ))

        # ===== Schritt 7: Gesamtbetrag =====
        schritt_nr += 1
        gesamt = zwischensumme + ust

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Gesamtbetrag brutto",
            formel="Zwischensumme + Umsatzsteuer",
            eingabewerte={
                "zwischensumme": zwischensumme,
                "umsatzsteuer": ust
            },
            ergebnis=round(gesamt, 2),
            erlaeuterung=None
        ))

        # ===== Ergebnis =====
        ergebnis_dict = {
            "gegenstandswert": eingabe.gegenstandswert,
            "wertgebuehr": wertgebuehr,
            "faktor": eingabe.faktor,
            "gebuehr_netto": round(gebuehr, 2),
            "auslagen": auslagen,
            "zwischensumme": round(zwischensumme, 2),
            "umsatzsteuer": round(ust, 2),
            "gesamt_brutto": round(gesamt, 2)
        }

        eingabe_dict = {
            "gegenstandswert": eingabe.gegenstandswert,
            "gebuehrenart": eingabe.gebuehrenart,
            "faktor": eingabe.faktor,
            "mehrere_auftraggeber": eingabe.mehrere_auftraggeber,
            "auslagen_pauschale": eingabe.auslagen_pauschale,
            "umsatzsteuer": eingabe.umsatzsteuer
        }

        ruleset = RulesetInfo(
            olg_bezirk="Bundesrecht",
            version="RVG 2021",
            gueltig_ab=date(2021, 1, 1),
            parameter={"tabelle": "Anlage 2 zu § 13 RVG"}
        )

        return CalculationResult(
            berechnungstyp=BerechnungsTyp.RVG,
            eingabewerte=eingabe_dict,
            ergebnis=ergebnis_dict,
            schritte=schritte,
            ruleset=ruleset,
            duesseldorfer_tabelle_stand=date(2025, 1, 1),
            warnungen=warnungen
        )


def calculate_rvg_fee(
    gegenstandswert: float,
    faktor: float = 1.3,
    gebuehrenart: str = "verfahren"
) -> CalculationResult:
    """Vereinfachte RVG-Berechnung"""
    eingabe = RVGEingabe(
        gegenstandswert=gegenstandswert,
        gebuehrenart=gebuehrenart,
        faktor=faktor
    )
    calculator = RVGCalculator()
    return calculator.berechne(eingabe)
