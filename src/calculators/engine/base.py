"""
FamilyKom Calculation Engine - Basis-Klassen
============================================

Grundlegende Datenstrukturen fuer alle Berechnungen.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class BerechnungsTyp(Enum):
    """Typen von Berechnungen"""
    KINDESUNTERHALT = "kindesunterhalt"
    TRENNUNGSUNTERHALT = "trennungsunterhalt"
    NACHEHELICHER_UNTERHALT = "nachehelicher_unterhalt"
    ZUGEWINN = "zugewinn"
    RVG = "rvg"


@dataclass
class RulesetInfo:
    """Informationen zum verwendeten Regelwerk"""
    olg_bezirk: str
    version: str
    gueltig_ab: date
    parameter: Dict[str, Any]

    def to_dict(self) -> Dict:
        return {
            "olg_bezirk": self.olg_bezirk,
            "version": self.version,
            "gueltig_ab": self.gueltig_ab.isoformat(),
            "parameter": self.parameter
        }


@dataclass
class CalculationStep:
    """Ein einzelner Berechnungsschritt"""
    schritt_nr: int
    bezeichnung: str
    formel: str
    eingabewerte: Dict[str, Any]
    ergebnis: Any
    erlaeuterung: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "schritt_nr": self.schritt_nr,
            "bezeichnung": self.bezeichnung,
            "formel": self.formel,
            "eingabewerte": self.eingabewerte,
            "ergebnis": self.ergebnis,
            "erlaeuterung": self.erlaeuterung
        }


@dataclass
class CalculationWarning:
    """Warnung bei einer Berechnung"""
    code: str
    message: str
    severity: str = "warning"  # "info", "warning", "error"

    def to_dict(self) -> Dict:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity
        }


@dataclass
class CalculationResult:
    """Ergebnis einer Berechnung mit vollstaendiger Dokumentation"""
    berechnungstyp: BerechnungsTyp
    eingabewerte: Dict[str, Any]
    ergebnis: Dict[str, Any]
    schritte: List[CalculationStep]
    ruleset: RulesetInfo
    duesseldorfer_tabelle_stand: date
    warnungen: List[CalculationWarning] = field(default_factory=list)
    berechnet_am: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Konvertiert das Ergebnis in ein serialisierbares Dictionary"""
        return {
            "berechnungstyp": self.berechnungstyp.value,
            "eingabewerte": self.eingabewerte,
            "ergebnis": self.ergebnis,
            "schritte": [s.to_dict() for s in self.schritte],
            "ruleset": self.ruleset.to_dict(),
            "duesseldorfer_tabelle_stand": self.duesseldorfer_tabelle_stand.isoformat(),
            "warnungen": [w.to_dict() for w in self.warnungen],
            "berechnet_am": self.berechnet_am.isoformat()
        }

    def to_json(self) -> str:
        """Konvertiert das Ergebnis in JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @property
    def hat_warnungen(self) -> bool:
        return len(self.warnungen) > 0

    @property
    def hat_fehler(self) -> bool:
        return any(w.severity == "error" for w in self.warnungen)


@dataclass
class Kind:
    """Daten eines Kindes fuer Unterhaltsberechnung"""
    vorname: str
    geburtsdatum: date
    lebt_bei: str  # 'mandant', 'gegner', 'abwechselnd'
    eigenes_einkommen: float = 0.0
    kindergeld_empfaenger: str = "gegner"  # wer bekommt Kindergeld
    privilegiert: bool = True  # § 1603 Abs. 2 BGB
    in_ausbildung: bool = False

    @property
    def alter(self) -> int:
        today = date.today()
        return today.year - self.geburtsdatum.year - (
            (today.month, today.day) < (self.geburtsdatum.month, self.geburtsdatum.day)
        )

    @property
    def altersstufe(self) -> int:
        """Altersstufe nach Duesseldorfer Tabelle"""
        alter = self.alter
        if alter < 6:
            return 0  # 0-5 Jahre
        elif alter < 12:
            return 1  # 6-11 Jahre
        elif alter < 18:
            return 2  # 12-17 Jahre
        else:
            return 3  # ab 18 Jahre

    @property
    def ist_minderjaehrig(self) -> bool:
        return self.alter < 18

    @property
    def ist_privilegiert_volljaehrig(self) -> bool:
        """Privilegierte Volljaehrige nach § 1603 Abs. 2 BGB"""
        return (
            not self.ist_minderjaehrig and
            self.alter < 21 and
            self.in_ausbildung and
            self.lebt_bei in ['mandant', 'gegner']  # lebt bei Elternteil
        )


@dataclass
class Einkommen:
    """Einkommensdaten fuer Unterhaltsberechnung"""
    brutto_monat: float
    netto_monat: float

    # Abzuege (bereits im Netto enthalten oder zusaetzlich)
    berufsbedingte_aufwendungen: Optional[float] = None
    zusaetzliche_altersvorsorge: Optional[float] = None
    schulden_tilgung: Optional[float] = None
    weitere_unterhaltspflichten: Optional[float] = None
    umgangskosten: Optional[float] = None

    # Besonderheiten
    ist_selbstaendig: bool = False
    einmalzahlungen_jahres_anteil: float = 0.0


@dataclass
class Vermoegen:
    """Vermoegensposition fuer Zugewinnberechnung"""
    bezeichnung: str
    kategorie: str  # 'immobilie', 'fahrzeug', 'konto', 'wertpapier', 'unternehmen', 'sonstig'
    wert: float
    eigentuemer: str  # 'mandant', 'gegner', 'gemeinsam'
    stichtag: date
    ist_privilegiert: bool = False  # Erbschaft/Schenkung
    verbindlichkeit: float = 0.0
