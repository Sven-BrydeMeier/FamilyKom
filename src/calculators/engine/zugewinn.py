"""
FamilyKom Calculation Engine - Zugewinnausgleich
================================================

Berechnung des Zugewinnausgleichs nach §§ 1373-1378 BGB
mit vollstaendiger Dokumentation.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Any

from .base import (
    BerechnungsTyp, CalculationResult, CalculationStep,
    CalculationWarning, RulesetInfo, Vermoegen
)
from .ruleset import RulesetManager


@dataclass
class ZugewinnEingabe:
    """Eingabewerte fuer Zugewinn-Berechnung"""
    eheschliessung: date
    stichtag_endvermoegen: date  # meist Zustellung Scheidungsantrag

    # Vermoegen Mandant
    anfangsvermoegen_mandant: List[Vermoegen]
    endvermoegen_mandant: List[Vermoegen]

    # Vermoegen Gegner
    anfangsvermoegen_gegner: List[Vermoegen]
    endvermoegen_gegner: List[Vermoegen]

    # VPI-Indexierung
    vpi_eheschliessung: Optional[float] = None
    vpi_stichtag: Optional[float] = None


class ZugewinnCalculator:
    """Rechner fuer Zugewinnausgleich"""

    # VPI-Werte (Verbraucherpreisindex) - Auszug
    VPI_WERTE = {
        2020: 105.8,
        2021: 109.1,
        2022: 116.6,
        2023: 123.8,
        2024: 127.5,
        2025: 130.2,
        2026: 133.0,
    }

    def __init__(self):
        pass

    def get_vpi(self, jahr: int) -> float:
        """Gibt den VPI fuer ein Jahr zurueck"""
        return self.VPI_WERTE.get(jahr, 130.0)

    def indexiere_anfangsvermoegen(
        self,
        wert: float,
        von_datum: date,
        bis_datum: date,
        vpi_von: Optional[float] = None,
        vpi_bis: Optional[float] = None
    ) -> float:
        """Indexiert das Anfangsvermoegen auf den Stichtag"""
        vpi_von = vpi_von or self.get_vpi(von_datum.year)
        vpi_bis = vpi_bis or self.get_vpi(bis_datum.year)

        if vpi_von == 0:
            return wert

        faktor = vpi_bis / vpi_von
        return wert * faktor

    def berechne(self, eingabe: ZugewinnEingabe) -> CalculationResult:
        """
        Fuehrt die vollstaendige Zugewinn-Berechnung durch.

        Schritte:
        1. Anfangsvermoegen beider Ehegatten (indexiert)
        2. Endvermoegen beider Ehegatten
        3. Zugewinn je Ehegatte
        4. Ausgleichsanspruch (Haelfte der Differenz)
        """
        schritte: List[CalculationStep] = []
        warnungen: List[CalculationWarning] = []
        schritt_nr = 0

        # VPI-Werte
        vpi_anfang = eingabe.vpi_eheschliessung or self.get_vpi(eingabe.eheschliessung.year)
        vpi_ende = eingabe.vpi_stichtag or self.get_vpi(eingabe.stichtag_endvermoegen.year)

        # ===== Schritt 1: Anfangsvermoegen Mandant (indexiert) =====
        schritt_nr += 1

        av_mandant_roh = sum(v.wert - v.verbindlichkeit for v in eingabe.anfangsvermoegen_mandant)
        av_mandant_indexiert = self.indexiere_anfangsvermoegen(
            av_mandant_roh,
            eingabe.eheschliessung,
            eingabe.stichtag_endvermoegen,
            vpi_anfang,
            vpi_ende
        )
        # Negatives Anfangsvermoegen wird auf 0 gesetzt
        av_mandant = max(0, av_mandant_indexiert)

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Anfangsvermoegen Mandant (indexiert)",
            formel="Summe Vermoegen - Verbindlichkeiten, indexiert mit VPI",
            eingabewerte={
                "positionen": [
                    {"bezeichnung": v.bezeichnung, "wert": v.wert, "verbindlichkeit": v.verbindlichkeit}
                    for v in eingabe.anfangsvermoegen_mandant
                ],
                "summe_roh": av_mandant_roh,
                "vpi_anfang": vpi_anfang,
                "vpi_ende": vpi_ende
            },
            ergebnis=round(av_mandant, 2),
            erlaeuterung=f"Indexierungsfaktor: {vpi_ende/vpi_anfang:.4f}"
        ))

        # ===== Schritt 2: Anfangsvermoegen Gegner (indexiert) =====
        schritt_nr += 1

        av_gegner_roh = sum(v.wert - v.verbindlichkeit for v in eingabe.anfangsvermoegen_gegner)
        av_gegner_indexiert = self.indexiere_anfangsvermoegen(
            av_gegner_roh,
            eingabe.eheschliessung,
            eingabe.stichtag_endvermoegen,
            vpi_anfang,
            vpi_ende
        )
        av_gegner = max(0, av_gegner_indexiert)

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Anfangsvermoegen Gegner (indexiert)",
            formel="Summe Vermoegen - Verbindlichkeiten, indexiert mit VPI",
            eingabewerte={
                "positionen": [
                    {"bezeichnung": v.bezeichnung, "wert": v.wert, "verbindlichkeit": v.verbindlichkeit}
                    for v in eingabe.anfangsvermoegen_gegner
                ],
                "summe_roh": av_gegner_roh
            },
            ergebnis=round(av_gegner, 2),
            erlaeuterung="Negatives Anfangsvermoegen wird auf 0 gesetzt"
        ))

        # ===== Schritt 3: Endvermoegen Mandant =====
        schritt_nr += 1

        ev_mandant = sum(v.wert - v.verbindlichkeit for v in eingabe.endvermoegen_mandant)

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Endvermoegen Mandant",
            formel="Summe Vermoegen - Verbindlichkeiten zum Stichtag",
            eingabewerte={
                "positionen": [
                    {"bezeichnung": v.bezeichnung, "wert": v.wert, "verbindlichkeit": v.verbindlichkeit}
                    for v in eingabe.endvermoegen_mandant
                ],
                "stichtag": eingabe.stichtag_endvermoegen.isoformat()
            },
            ergebnis=round(ev_mandant, 2),
            erlaeuterung=f"Stichtag: {eingabe.stichtag_endvermoegen.strftime('%d.%m.%Y')}"
        ))

        # ===== Schritt 4: Endvermoegen Gegner =====
        schritt_nr += 1

        ev_gegner = sum(v.wert - v.verbindlichkeit for v in eingabe.endvermoegen_gegner)

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Endvermoegen Gegner",
            formel="Summe Vermoegen - Verbindlichkeiten zum Stichtag",
            eingabewerte={
                "positionen": [
                    {"bezeichnung": v.bezeichnung, "wert": v.wert, "verbindlichkeit": v.verbindlichkeit}
                    for v in eingabe.endvermoegen_gegner
                ]
            },
            ergebnis=round(ev_gegner, 2),
            erlaeuterung=None
        ))

        # ===== Schritt 5: Zugewinn berechnen =====
        schritt_nr += 1

        zugewinn_mandant = ev_mandant - av_mandant
        zugewinn_gegner = ev_gegner - av_gegner

        # Negativer Zugewinn = 0
        zugewinn_mandant = max(0, zugewinn_mandant)
        zugewinn_gegner = max(0, zugewinn_gegner)

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Zugewinn beider Ehegatten",
            formel="Endvermoegen - Anfangsvermoegen (mind. 0)",
            eingabewerte={
                "ev_mandant": ev_mandant,
                "av_mandant": av_mandant,
                "ev_gegner": ev_gegner,
                "av_gegner": av_gegner
            },
            ergebnis={
                "zugewinn_mandant": round(zugewinn_mandant, 2),
                "zugewinn_gegner": round(zugewinn_gegner, 2)
            },
            erlaeuterung="Negativer Zugewinn wird auf 0 gesetzt (§ 1373 BGB)"
        ))

        # ===== Schritt 6: Ausgleichsanspruch =====
        schritt_nr += 1

        differenz = zugewinn_gegner - zugewinn_mandant
        ausgleich = differenz / 2

        # Wer bekommt den Ausgleich?
        if ausgleich > 0:
            berechtigter = "Mandant"
            verpflichteter = "Gegner"
        elif ausgleich < 0:
            berechtigter = "Gegner"
            verpflichteter = "Mandant"
            ausgleich = abs(ausgleich)
        else:
            berechtigter = None
            verpflichteter = None

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Ausgleichsanspruch",
            formel="(Zugewinn B - Zugewinn A) / 2",
            eingabewerte={
                "zugewinn_mandant": zugewinn_mandant,
                "zugewinn_gegner": zugewinn_gegner
            },
            ergebnis={
                "differenz": round(differenz, 2),
                "ausgleichsbetrag": round(ausgleich, 2),
                "berechtigter": berechtigter,
                "verpflichteter": verpflichteter
            },
            erlaeuterung=f"Ausgleichsforderung: {ausgleich:.2f} EUR an {berechtigter}" if berechtigter else "Kein Ausgleich"
        ))

        # Warnungen
        if ev_mandant < 0 or ev_gegner < 0:
            warnungen.append(CalculationWarning(
                code="NEGATIVES_ENDVERMOEGEN",
                message="Das Endvermoegen eines Ehegatten ist negativ. Pruefung auf Illoyalitaet empfohlen.",
                severity="warning"
            ))

        # ===== Ergebnis zusammenstellen =====
        ergebnis_dict = {
            "anfangsvermoegen_mandant": round(av_mandant, 2),
            "anfangsvermoegen_gegner": round(av_gegner, 2),
            "endvermoegen_mandant": round(ev_mandant, 2),
            "endvermoegen_gegner": round(ev_gegner, 2),
            "zugewinn_mandant": round(zugewinn_mandant, 2),
            "zugewinn_gegner": round(zugewinn_gegner, 2),
            "differenz": round(differenz, 2),
            "ausgleichsbetrag": round(ausgleich, 2),
            "berechtigter": berechtigter,
            "verpflichteter": verpflichteter,
            "vpi_faktor": round(vpi_ende / vpi_anfang, 4)
        }

        eingabe_dict = {
            "eheschliessung": eingabe.eheschliessung.isoformat(),
            "stichtag_endvermoegen": eingabe.stichtag_endvermoegen.isoformat(),
            "vpi_anfang": vpi_anfang,
            "vpi_ende": vpi_ende
        }

        # Dummy Ruleset fuer Zugewinn
        ruleset = RulesetInfo(
            olg_bezirk="Bundesrecht",
            version="2025.1",
            gueltig_ab=date(2025, 1, 1),
            parameter={"vpi_indexierung": True}
        )

        return CalculationResult(
            berechnungstyp=BerechnungsTyp.ZUGEWINN,
            eingabewerte=eingabe_dict,
            ergebnis=ergebnis_dict,
            schritte=schritte,
            ruleset=ruleset,
            duesseldorfer_tabelle_stand=date(2025, 1, 1),
            warnungen=warnungen
        )


def calculate_gain_equalization(
    eheschliessung: date,
    stichtag: date,
    av_mandant: float,
    ev_mandant: float,
    av_gegner: float,
    ev_gegner: float
) -> CalculationResult:
    """
    Vereinfachte Funktion zur Zugewinn-Berechnung.
    """
    eingabe = ZugewinnEingabe(
        eheschliessung=eheschliessung,
        stichtag_endvermoegen=stichtag,
        anfangsvermoegen_mandant=[
            Vermoegen(
                bezeichnung="Anfangsvermoegen gesamt",
                kategorie="sonstig",
                wert=av_mandant,
                eigentuemer="mandant",
                stichtag=eheschliessung
            )
        ],
        endvermoegen_mandant=[
            Vermoegen(
                bezeichnung="Endvermoegen gesamt",
                kategorie="sonstig",
                wert=ev_mandant,
                eigentuemer="mandant",
                stichtag=stichtag
            )
        ],
        anfangsvermoegen_gegner=[
            Vermoegen(
                bezeichnung="Anfangsvermoegen gesamt",
                kategorie="sonstig",
                wert=av_gegner,
                eigentuemer="gegner",
                stichtag=eheschliessung
            )
        ],
        endvermoegen_gegner=[
            Vermoegen(
                bezeichnung="Endvermoegen gesamt",
                kategorie="sonstig",
                wert=ev_gegner,
                eigentuemer="gegner",
                stichtag=stichtag
            )
        ]
    )

    calculator = ZugewinnCalculator()
    return calculator.berechne(eingabe)
