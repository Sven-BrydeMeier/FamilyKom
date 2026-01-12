"""
FamilyKom Calculation Engine - Kindesunterhalt
===============================================

Berechnung des Kindesunterhalts nach Duesseldorfer Tabelle
und OLG-Leitlinien mit vollstaendiger Dokumentation.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Any
from decimal import Decimal, ROUND_HALF_UP

from .base import (
    BerechnungsTyp, CalculationResult, CalculationStep,
    CalculationWarning, RulesetInfo, Kind, Einkommen
)
from .ruleset import RulesetManager


@dataclass
class KindesunterhaltEingabe:
    """Eingabewerte fuer Kindesunterhalt-Berechnung"""
    pflichtiger_einkommen: Einkommen
    kinder: List[Kind]
    olg_bezirk: str = "Schleswig"
    pflichtiger_erwerbstaetig: bool = True
    stichtag: Optional[date] = None


@dataclass
class KindesunterhaltErgebnis:
    """Ergebnis der Kindesunterhalt-Berechnung pro Kind"""
    kind_vorname: str
    kind_alter: int
    altersstufe: int
    einkommensgruppe: int
    tabellenbetrag: int
    kindergeld_abzug: int
    zahlbetrag: int
    ist_mangelfall: bool = False
    mangelfall_zahlbetrag: Optional[int] = None


class KindesunterhaltCalculator:
    """Rechner fuer Kindesunterhalt nach Duesseldorfer Tabelle"""

    def __init__(self, olg_bezirk: str = "Schleswig"):
        self.olg_bezirk = olg_bezirk
        self.ruleset = RulesetManager.get_ruleset(olg_bezirk)

    def berechne(self, eingabe: KindesunterhaltEingabe) -> CalculationResult:
        """
        Fuehrt die vollstaendige Kindesunterhalt-Berechnung durch.

        Schritte:
        1. Bereinigtes Nettoeinkommen ermitteln
        2. Einkommensgruppe bestimmen
        3. ggf. Herabstufung bei mehreren Berechtigten
        4. Tabellenbedarf pro Kind nach Altersstufe
        5. Kindergeldanrechnung
        6. Leistungsfaehigkeitspruefung (Selbstbehalt)
        7. ggf. Mangelfallberechnung
        """
        schritte: List[CalculationStep] = []
        warnungen: List[CalculationWarning] = []
        schritt_nr = 0

        stichtag = eingabe.stichtag or date.today()
        dt = RulesetManager.get_duesseldorfer_tabelle(stichtag)

        # ===== Schritt 1: Bereinigtes Nettoeinkommen =====
        schritt_nr += 1
        einkommen = eingabe.pflichtiger_einkommen

        # Berufsbedingte Aufwendungen
        berufsbed = RulesetManager.get_berufsbedingte_aufwendungen(
            einkommen.netto_monat,
            self.olg_bezirk,
            einkommen.berufsbedingte_aufwendungen
        )

        # Bereinigung
        bereinigt = einkommen.netto_monat

        # Abzuege
        abzuege = {
            "berufsbedingte_aufwendungen": berufsbed,
        }

        if einkommen.zusaetzliche_altersvorsorge:
            abzuege["zusaetzliche_altersvorsorge"] = einkommen.zusaetzliche_altersvorsorge
        if einkommen.schulden_tilgung:
            abzuege["schulden_tilgung"] = einkommen.schulden_tilgung
        if einkommen.umgangskosten:
            abzuege["umgangskosten"] = einkommen.umgangskosten

        bereinigt -= sum(abzuege.values())

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Bereinigtes Nettoeinkommen",
            formel="Netto - berufsbedingte Aufwendungen - sonstige Abzuege",
            eingabewerte={
                "netto_monat": einkommen.netto_monat,
                "abzuege": abzuege
            },
            ergebnis=round(bereinigt, 2),
            erlaeuterung=f"Bereinigtes Netto: {bereinigt:.2f} EUR"
        ))

        # ===== Schritt 2: Einkommensgruppe bestimmen =====
        schritt_nr += 1
        einkommensgruppe = RulesetManager.get_einkommensgruppe(bereinigt, stichtag)

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Einkommensgruppe nach Duesseldorfer Tabelle",
            formel="Zuordnung des bereinigten Nettos zu Einkommensgruppe",
            eingabewerte={"bereinigtes_netto": bereinigt},
            ergebnis=einkommensgruppe,
            erlaeuterung=f"Einkommensgruppe {einkommensgruppe} (Stand: {dt['stand'].isoformat()})"
        ))

        # ===== Schritt 3: Herabstufung pruefen =====
        schritt_nr += 1
        anzahl_berechtigte = len(eingabe.kinder)
        angepasste_gruppe = einkommensgruppe

        herabstufung_params = self.ruleset.parameter.get("herabstufung", {})
        ab_anzahl = herabstufung_params.get("ab_anzahl", 4)
        stufen = herabstufung_params.get("stufen", 1)

        if anzahl_berechtigte >= ab_anzahl:
            angepasste_gruppe = max(1, einkommensgruppe - stufen)
            schritte.append(CalculationStep(
                schritt_nr=schritt_nr,
                bezeichnung="Herabstufung bei mehreren Berechtigten",
                formel=f"Bei >= {ab_anzahl} Berechtigten: Herabstufung um {stufen} Stufe(n)",
                eingabewerte={
                    "anzahl_berechtigte": anzahl_berechtigte,
                    "urspruengliche_gruppe": einkommensgruppe
                },
                ergebnis=angepasste_gruppe,
                erlaeuterung=f"Herabstufung von Gruppe {einkommensgruppe} auf {angepasste_gruppe}"
            ))
        else:
            schritte.append(CalculationStep(
                schritt_nr=schritt_nr,
                bezeichnung="Herabstufung pruefen",
                formel=f"Herabstufung nur bei >= {ab_anzahl} Berechtigten",
                eingabewerte={"anzahl_berechtigte": anzahl_berechtigte},
                ergebnis="keine_herabstufung",
                erlaeuterung=f"Keine Herabstufung bei {anzahl_berechtigte} Berechtigten"
            ))

        # ===== Schritt 4-6: Berechnung pro Kind =====
        kindergeld = RulesetManager.get_kindergeld(stichtag)
        kinder_ergebnisse: List[KindesunterhaltErgebnis] = []
        gesamt_bedarf = 0

        for kind in eingabe.kinder:
            schritt_nr += 1

            # Tabellenbetrag
            tabellenbetrag = RulesetManager.get_tabellenbetrag(
                angepasste_gruppe,
                kind.altersstufe,
                stichtag
            )

            # Kindergeldanrechnung
            # Bei Minderjährigen: halbes Kindergeld
            # Bei Volljährigen: volles Kindergeld
            if kind.ist_minderjaehrig:
                kg_abzug = kindergeld // 2
            else:
                kg_abzug = kindergeld

            # Zahlbetrag
            zahlbetrag = tabellenbetrag - kg_abzug

            # Eigenes Einkommen anrechnen (bei Volljaehrigen voll, bei Minderjaehrigen halb)
            if kind.eigenes_einkommen > 0:
                if kind.ist_minderjaehrig:
                    anrechnung = kind.eigenes_einkommen / 2
                else:
                    anrechnung = kind.eigenes_einkommen
                zahlbetrag -= int(anrechnung)

            zahlbetrag = max(0, zahlbetrag)
            gesamt_bedarf += zahlbetrag

            schritte.append(CalculationStep(
                schritt_nr=schritt_nr,
                bezeichnung=f"Berechnung fuer {kind.vorname}",
                formel="Tabellenbetrag - Kindergeldanrechnung - eigenes Einkommen",
                eingabewerte={
                    "alter": kind.alter,
                    "altersstufe": kind.altersstufe,
                    "einkommensgruppe": angepasste_gruppe,
                    "tabellenbetrag": tabellenbetrag,
                    "kindergeld_abzug": kg_abzug,
                    "eigenes_einkommen": kind.eigenes_einkommen
                },
                ergebnis=zahlbetrag,
                erlaeuterung=f"{kind.vorname} ({kind.alter} J.): Zahlbetrag {zahlbetrag} EUR"
            ))

            kinder_ergebnisse.append(KindesunterhaltErgebnis(
                kind_vorname=kind.vorname,
                kind_alter=kind.alter,
                altersstufe=kind.altersstufe,
                einkommensgruppe=angepasste_gruppe,
                tabellenbetrag=tabellenbetrag,
                kindergeld_abzug=kg_abzug,
                zahlbetrag=zahlbetrag
            ))

        # ===== Schritt 7: Leistungsfaehigkeitspruefung =====
        schritt_nr += 1

        selbstbehalt = RulesetManager.get_selbstbehalt(
            self.olg_bezirk,
            "minderjaehrig",
            eingabe.pflichtiger_erwerbstaetig
        )

        verfuegbar = bereinigt - selbstbehalt
        ist_mangelfall = verfuegbar < gesamt_bedarf

        schritte.append(CalculationStep(
            schritt_nr=schritt_nr,
            bezeichnung="Leistungsfaehigkeitspruefung",
            formel="Bereinigtes Netto - Selbstbehalt = verfuegbare Masse",
            eingabewerte={
                "bereinigtes_netto": bereinigt,
                "selbstbehalt": selbstbehalt,
                "gesamt_bedarf": gesamt_bedarf
            },
            ergebnis={
                "verfuegbar": round(verfuegbar, 2),
                "ist_mangelfall": ist_mangelfall
            },
            erlaeuterung=f"Verfuegbar: {verfuegbar:.2f} EUR, Bedarf: {gesamt_bedarf} EUR"
        ))

        # ===== Schritt 8: Mangelfallberechnung (falls erforderlich) =====
        if ist_mangelfall:
            schritt_nr += 1
            warnungen.append(CalculationWarning(
                code="MANGELFALL",
                message="Es liegt ein Mangelfall vor. Die Zahlbetraege werden anteilig gekuerzt.",
                severity="warning"
            ))

            # Quotenmethode: Verteilung nach Bedarf
            if gesamt_bedarf > 0:
                quote = verfuegbar / gesamt_bedarf
            else:
                quote = 0

            for ergebnis in kinder_ergebnisse:
                ergebnis.ist_mangelfall = True
                ergebnis.mangelfall_zahlbetrag = max(0, int(ergebnis.zahlbetrag * quote))

            schritte.append(CalculationStep(
                schritt_nr=schritt_nr,
                bezeichnung="Mangelfallberechnung",
                formel="Verfuegbare Masse / Gesamtbedarf = Quote",
                eingabewerte={
                    "verfuegbar": verfuegbar,
                    "gesamt_bedarf": gesamt_bedarf
                },
                ergebnis={
                    "quote": round(quote, 4),
                    "gekuerzte_betraege": {
                        e.kind_vorname: e.mangelfall_zahlbetrag
                        for e in kinder_ergebnisse
                    }
                },
                erlaeuterung=f"Kuerzungsquote: {quote:.2%}"
            ))

        # ===== Ergebnis zusammenstellen =====
        gesamt_zahlbetrag = sum(
            e.mangelfall_zahlbetrag if e.ist_mangelfall else e.zahlbetrag
            for e in kinder_ergebnisse
        )

        ergebnis_dict = {
            "kinder": [
                {
                    "vorname": e.kind_vorname,
                    "alter": e.kind_alter,
                    "altersstufe": e.altersstufe,
                    "tabellenbetrag": e.tabellenbetrag,
                    "kindergeld_abzug": e.kindergeld_abzug,
                    "zahlbetrag": e.zahlbetrag,
                    "ist_mangelfall": e.ist_mangelfall,
                    "mangelfall_zahlbetrag": e.mangelfall_zahlbetrag
                }
                for e in kinder_ergebnisse
            ],
            "gesamt_zahlbetrag": gesamt_zahlbetrag,
            "ist_mangelfall": ist_mangelfall,
            "bereinigtes_netto": round(bereinigt, 2),
            "einkommensgruppe": angepasste_gruppe,
            "selbstbehalt": selbstbehalt
        }

        eingabe_dict = {
            "pflichtiger_netto": eingabe.pflichtiger_einkommen.netto_monat,
            "pflichtiger_brutto": eingabe.pflichtiger_einkommen.brutto_monat,
            "pflichtiger_erwerbstaetig": eingabe.pflichtiger_erwerbstaetig,
            "kinder": [
                {
                    "vorname": k.vorname,
                    "geburtsdatum": k.geburtsdatum.isoformat(),
                    "lebt_bei": k.lebt_bei,
                    "eigenes_einkommen": k.eigenes_einkommen
                }
                for k in eingabe.kinder
            ],
            "olg_bezirk": eingabe.olg_bezirk,
            "stichtag": stichtag.isoformat()
        }

        return CalculationResult(
            berechnungstyp=BerechnungsTyp.KINDESUNTERHALT,
            eingabewerte=eingabe_dict,
            ergebnis=ergebnis_dict,
            schritte=schritte,
            ruleset=self.ruleset,
            duesseldorfer_tabelle_stand=dt["stand"],
            warnungen=warnungen
        )


def calculate_child_support(
    pflichtiger_netto: float,
    pflichtiger_brutto: float,
    kinder_daten: List[Dict],
    olg_bezirk: str = "Schleswig",
    erwerbstaetig: bool = True,
    stichtag: Optional[date] = None
) -> CalculationResult:
    """
    Vereinfachte Funktion zur Kindesunterhalt-Berechnung.

    Args:
        pflichtiger_netto: Monatliches Nettoeinkommen des Pflichtigen
        pflichtiger_brutto: Monatliches Bruttoeinkommen des Pflichtigen
        kinder_daten: Liste von Dicts mit {vorname, geburtsdatum, lebt_bei, eigenes_einkommen}
        olg_bezirk: OLG-Bezirk fuer Leitlinien
        erwerbstaetig: Ob der Pflichtige erwerbstaetig ist
        stichtag: Berechnungsstichtag

    Returns:
        CalculationResult mit allen Zwischenschritten
    """
    kinder = [
        Kind(
            vorname=k.get("vorname", "Kind"),
            geburtsdatum=k.get("geburtsdatum") if isinstance(k.get("geburtsdatum"), date)
                else date.fromisoformat(k.get("geburtsdatum", "2020-01-01")),
            lebt_bei=k.get("lebt_bei", "gegner"),
            eigenes_einkommen=k.get("eigenes_einkommen", 0),
            kindergeld_empfaenger=k.get("kindergeld_empfaenger", "gegner"),
            privilegiert=k.get("privilegiert", True),
            in_ausbildung=k.get("in_ausbildung", False)
        )
        for k in kinder_daten
    ]

    eingabe = KindesunterhaltEingabe(
        pflichtiger_einkommen=Einkommen(
            brutto_monat=pflichtiger_brutto,
            netto_monat=pflichtiger_netto
        ),
        kinder=kinder,
        olg_bezirk=olg_bezirk,
        pflichtiger_erwerbstaetig=erwerbstaetig,
        stichtag=stichtag
    )

    calculator = KindesunterhaltCalculator(olg_bezirk)
    return calculator.berechne(eingabe)
