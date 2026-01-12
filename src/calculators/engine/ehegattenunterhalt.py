"""
FamilyKom Calculation Engine - Ehegattenunterhalt
=================================================

Berechnung des Trennungs- und nachehelichen Unterhalts
nach OLG-Leitlinien mit vollstaendiger Dokumentation.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Any

from .base import (
    BerechnungsTyp, CalculationResult, CalculationStep,
    CalculationWarning, RulesetInfo, Einkommen
)
from .ruleset import RulesetManager


@dataclass
class EhegattenunterhaltEingabe:
    """Eingabewerte fuer Ehegattenunterhalt-Berechnung"""
    berechtigter_einkommen: Einkommen
    pflichtiger_einkommen: Einkommen
    olg_bezirk: str = "Schleswig"
    unterhaltsart: str = "trennungsunterhalt"  # oder "nachehelich"
    berechtigter_erwerbstaetig: bool = False
    pflichtiger_erwerbstaetig: bool = True
    kindesunterhalt_abzug: float = 0.0  # vorrangiger Kindesunterhalt
    wohnvorteil_berechtigter: float = 0.0
    wohnvorteil_pflichtiger: float = 0.0
    stichtag: Optional[date] = None


class EhegattenunterhaltCalculator:
    """Rechner fuer Trennungs- und nachehelichen Unterhalt"""

    def __init__(self, olg_bezirk: str = "Schleswig"):
        self.olg_bezirk = olg_bezirk
        self.ruleset = RulesetManager.get_ruleset(olg_bezirk)

    def berechne(self, eingabe: EhegattenunterhaltEingabe) -> CalculationResult:
        """
        Fuehrt die vollstaendige Ehegattenunterhalt-Berechnung durch.

        Schritte:
        1. Bereinigte Einkommen beider Ehegatten ermitteln
        2. Vorrangigen Kindesunterhalt abziehen
        3. Differenz / Halbteilung mit Erwerbstaetigenbonus
        4. Selbstbehaltspruefung
        5. Zahlbetrag ermitteln
        """
        schritte: List[CalculationStep] = []
        warnungen: List[CalculationWarning] = []
        schritt_nr = 0

        stichtag = eingabe.stichtag or date.today()
        dt = RulesetManager.get_duesseldorfer_tabelle(stichtag)

        # ===== Schritt 1: Bereinigte Einkommen =====
        schritt_nr += 1

        # Berufsbedingte Aufwendungen
        berufsbed_pflichtiger = RulesetManager.get_berufsbedingte_aufwendungen(
            eingabe.pflichtiger_einkommen.netto_monat,
            self.olg_bezirk
        )
        berufsbed_berechtigter = RulesetManager.get_berufsbedingte_aufwendungen(
            eingabe.berechtigter_einkommen.netto_monat,
            self.olg_bezirk
        ) if eingabe.berechtigter_einkommen.netto_monat > 0 else 0

        bereinigt_pflichtiger = (
            eingabe.pflichtiger_einkommen.netto_monat
            - berufsbed_pflichtiger
            + eingabe.wohnvorteil_pflichtiger
        )

        bereinigt_berechtigter = (
            eingabe.berechtigter_einkommen.netto_monat
            - berufsbed_berechtigter
            + eingabe.wohnvorteil_berechtigter
        )

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Bereinigte Einkommen",
            formel="Netto - berufsbedingte Aufwendungen + Wohnvorteil",
            eingabewerte={
                "pflichtiger_netto": eingabe.pflichtiger_einkommen.netto_monat,
                "pflichtiger_berufsbed": berufsbed_pflichtiger,
                "pflichtiger_wohnvorteil": eingabe.wohnvorteil_pflichtiger,
                "berechtigter_netto": eingabe.berechtigter_einkommen.netto_monat,
                "berechtigter_berufsbed": berufsbed_berechtigter,
                "berechtigter_wohnvorteil": eingabe.wohnvorteil_berechtigter,
            },
            ergebnis={
                "bereinigt_pflichtiger": round(bereinigt_pflichtiger, 2),
                "bereinigt_berechtigter": round(bereinigt_berechtigter, 2)
            },
            erlaeuterung="Bereinigte Einkommen beider Ehegatten"
        ))

        # ===== Schritt 2: Kindesunterhalt abziehen =====
        schritt_nr += 1

        pflichtiger_nach_kindesunterhalt = bereinigt_pflichtiger - eingabe.kindesunterhalt_abzug

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Abzug vorrangiger Kindesunterhalt",
            formel="Bereinigtes Einkommen - Kindesunterhalt",
            eingabewerte={
                "bereinigt_pflichtiger": bereinigt_pflichtiger,
                "kindesunterhalt": eingabe.kindesunterhalt_abzug
            },
            ergebnis=round(pflichtiger_nach_kindesunterhalt, 2),
            erlaeuterung="Kindesunterhalt ist vorrangig (§ 1609 BGB)"
        ))

        # ===== Schritt 3: Differenzmethode mit Erwerbstaetigenbonus =====
        schritt_nr += 1

        bonus_quote = RulesetManager.get_erwerbstaetigenbonus(self.olg_bezirk)

        # Erwerbstaetigenbonus nur fuer den Erwerbstaetigen
        if eingabe.pflichtiger_erwerbstaetig and not eingabe.berechtigter_erwerbstaetig:
            # Nur Pflichtiger arbeitet: Bonus fuer Pflichtigen
            bonus_pflichtiger = pflichtiger_nach_kindesunterhalt * bonus_quote
            verteilungsmasse = pflichtiger_nach_kindesunterhalt - bonus_pflichtiger
            bedarf_berechtigter = verteilungsmasse / 2

        elif eingabe.berechtigter_erwerbstaetig and not eingabe.pflichtiger_erwerbstaetig:
            # Nur Berechtigter arbeitet: Bonus fuer Berechtigten
            bonus_berechtigter = bereinigt_berechtigter * bonus_quote
            verteilungsmasse = pflichtiger_nach_kindesunterhalt + bereinigt_berechtigter - bonus_berechtigter
            bedarf_berechtigter = verteilungsmasse / 2

        elif eingabe.pflichtiger_erwerbstaetig and eingabe.berechtigter_erwerbstaetig:
            # Beide arbeiten: Beide behalten ihren Bonus
            bonus_pflichtiger = pflichtiger_nach_kindesunterhalt * bonus_quote
            bonus_berechtigter = bereinigt_berechtigter * bonus_quote
            verteilungsmasse = (
                pflichtiger_nach_kindesunterhalt - bonus_pflichtiger +
                bereinigt_berechtigter - bonus_berechtigter
            )
            bedarf_berechtigter = verteilungsmasse / 2 + bonus_berechtigter
        else:
            # Keiner arbeitet
            verteilungsmasse = pflichtiger_nach_kindesunterhalt + bereinigt_berechtigter
            bedarf_berechtigter = verteilungsmasse / 2

        # Unterhaltsbetrag = Bedarf - eigenes Einkommen
        unterhalt = bedarf_berechtigter - bereinigt_berechtigter
        unterhalt = max(0, unterhalt)

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Differenzmethode mit Erwerbstaetigenbonus",
            formel="(Gesamteinkommen - Erwerbstaetigenbonus) / 2 = Bedarf; Bedarf - eigenes Einkommen = Unterhalt",
            eingabewerte={
                "pflichtiger_nach_ku": pflichtiger_nach_kindesunterhalt,
                "berechtigter_bereinigt": bereinigt_berechtigter,
                "bonus_quote": bonus_quote
            },
            ergebnis={
                "bedarf_berechtigter": round(bedarf_berechtigter, 2),
                "unterhaltsbetrag": round(unterhalt, 2)
            },
            erlaeuterung=f"Erwerbstaetigenbonus: {bonus_quote:.2%} (1/7)"
        ))

        # ===== Schritt 4: Selbstbehaltspruefung =====
        schritt_nr += 1

        selbstbehalt = RulesetManager.get_selbstbehalt(
            self.olg_bezirk,
            "ehegatte",
            eingabe.pflichtiger_erwerbstaetig
        )

        verfuegbar = pflichtiger_nach_kindesunterhalt - selbstbehalt
        leistungsfaehig = verfuegbar >= unterhalt

        if not leistungsfaehig and unterhalt > 0:
            zahlbetrag = max(0, verfuegbar)
            warnungen.append(CalculationWarning(
                code="LEISTUNGSFAEHIGKEIT",
                message=f"Der Pflichtige kann nur {zahlbetrag:.2f} EUR zahlen (Selbstbehalt: {selbstbehalt} EUR)",
                severity="warning"
            ))
        else:
            zahlbetrag = unterhalt

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Leistungsfaehigkeitspruefung",
            formel="Einkommen nach Kindesunterhalt - Selbstbehalt = verfuegbar",
            eingabewerte={
                "einkommen_nach_ku": pflichtiger_nach_kindesunterhalt,
                "selbstbehalt": selbstbehalt,
                "unterhaltsbetrag": unterhalt
            },
            ergebnis={
                "verfuegbar": round(verfuegbar, 2),
                "leistungsfaehig": leistungsfaehig,
                "zahlbetrag": round(zahlbetrag, 2)
            },
            erlaeuterung=f"Selbstbehalt gegenueber Ehegatten: {selbstbehalt} EUR"
        ))

        # ===== Ergebnis zusammenstellen =====
        ergebnis_dict = {
            "unterhaltsart": eingabe.unterhaltsart,
            "bedarf_berechtigter": round(bedarf_berechtigter, 2),
            "unterhaltsbetrag": round(unterhalt, 2),
            "zahlbetrag": round(zahlbetrag, 2),
            "selbstbehalt": selbstbehalt,
            "leistungsfaehig": leistungsfaehig,
            "bereinigt_pflichtiger": round(bereinigt_pflichtiger, 2),
            "bereinigt_berechtigter": round(bereinigt_berechtigter, 2),
        }

        eingabe_dict = {
            "pflichtiger_netto": eingabe.pflichtiger_einkommen.netto_monat,
            "berechtigter_netto": eingabe.berechtigter_einkommen.netto_monat,
            "pflichtiger_erwerbstaetig": eingabe.pflichtiger_erwerbstaetig,
            "berechtigter_erwerbstaetig": eingabe.berechtigter_erwerbstaetig,
            "kindesunterhalt_abzug": eingabe.kindesunterhalt_abzug,
            "unterhaltsart": eingabe.unterhaltsart,
            "olg_bezirk": eingabe.olg_bezirk,
            "stichtag": stichtag.isoformat()
        }

        return CalculationResult(
            berechnungstyp=BerechnungsTyp.TRENNUNGSUNTERHALT if eingabe.unterhaltsart == "trennungsunterhalt"
                else BerechnungsTyp.NACHEHELICHER_UNTERHALT,
            eingabewerte=eingabe_dict,
            ergebnis=ergebnis_dict,
            schritte=schritte,
            ruleset=self.ruleset,
            duesseldorfer_tabelle_stand=dt["stand"],
            warnungen=warnungen
        )


def calculate_spousal_support(
    pflichtiger_netto: float,
    berechtigter_netto: float,
    kindesunterhalt_abzug: float = 0.0,
    unterhaltsart: str = "trennungsunterhalt",
    olg_bezirk: str = "Schleswig",
    pflichtiger_erwerbstaetig: bool = True,
    berechtigter_erwerbstaetig: bool = False,
    stichtag: Optional[date] = None
) -> CalculationResult:
    """
    Vereinfachte Funktion zur Ehegattenunterhalt-Berechnung.
    """
    eingabe = EhegattenunterhaltEingabe(
        berechtigter_einkommen=Einkommen(brutto_monat=0, netto_monat=berechtigter_netto),
        pflichtiger_einkommen=Einkommen(brutto_monat=0, netto_monat=pflichtiger_netto),
        olg_bezirk=olg_bezirk,
        unterhaltsart=unterhaltsart,
        berechtigter_erwerbstaetig=berechtigter_erwerbstaetig,
        pflichtiger_erwerbstaetig=pflichtiger_erwerbstaetig,
        kindesunterhalt_abzug=kindesunterhalt_abzug,
        stichtag=stichtag
    )

    calculator = EhegattenunterhaltCalculator(olg_bezirk)
    return calculator.berechne(eingabe)
