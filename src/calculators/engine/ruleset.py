"""
FamilyKom Calculation Engine - Ruleset Manager
===============================================

Verwaltung der OLG-Regelwerke und Duesseldorfer Tabelle.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Any
from .base import RulesetInfo


@dataclass
class DuesseldorferTabelleEintrag:
    """Ein Eintrag der Duesseldorfer Tabelle"""
    einkommensgruppe: int
    einkommen_von: int
    einkommen_bis: int
    betraege: Dict[int, int]  # Altersstufe -> Betrag
    bedarfskontrollbetrag: int


class RulesetManager:
    """Verwaltet OLG-Regelwerke und Duesseldorfer Tabelle"""

    # Duesseldorfer Tabelle 2025 (Stand 01.01.2025)
    DUESSELDORFER_TABELLE_2025 = {
        "stand": date(2025, 1, 1),
        "kindergeld": 255,  # EUR pro Kind/Monat
        "einkommensgruppen": {
            1: (0, 2100),
            2: (2101, 2500),
            3: (2501, 2900),
            4: (2901, 3300),
            5: (3301, 3700),
            6: (3701, 4100),
            7: (4101, 4500),
            8: (4501, 4900),
            9: (4901, 5300),
            10: (5301, 5700),
            11: (5701, 6400),
            12: (6401, 7200),
            13: (7201, 8200),
            14: (8201, 9700),
            15: (9701, 11200),
        },
        # Betraege: {Einkommensgruppe: {Altersstufe: Betrag}}
        "betraege": {
            1: {0: 482, 1: 554, 2: 649, 3: 693},
            2: {0: 507, 1: 582, 2: 682, 3: 728},
            3: {0: 531, 1: 610, 2: 714, 3: 763},
            4: {0: 555, 1: 638, 2: 747, 3: 797},
            5: {0: 579, 1: 665, 2: 779, 3: 832},
            6: {0: 617, 1: 710, 2: 831, 3: 888},
            7: {0: 656, 1: 754, 2: 883, 3: 943},
            8: {0: 695, 1: 798, 2: 935, 3: 998},
            9: {0: 733, 1: 843, 2: 987, 3: 1054},
            10: {0: 772, 1: 887, 2: 1039, 3: 1109},
            11: {0: 810, 1: 931, 2: 1090, 3: 1164},
            12: {0: 849, 1: 976, 2: 1142, 3: 1220},
            13: {0: 888, 1: 1020, 2: 1194, 3: 1275},
            14: {0: 927, 1: 1065, 2: 1247, 3: 1331},
            15: {0: 965, 1: 1109, 2: 1299, 3: 1387},
        },
        "bedarfskontrollbetraege": {
            1: 1200, 2: 1500, 3: 1600, 4: 1700, 5: 1800,
            6: 1900, 7: 2000, 8: 2100, 9: 2200, 10: 2300,
            11: 2400, 12: 2500, 13: 2600, 14: 2700, 15: 2800,
        },
    }

    # OLG Schleswig-Holstein Leitlinien 2025
    OLG_SCHLESWIG_2025 = {
        "olg_name": "Schleswig-Holsteinisches Oberlandesgericht",
        "olg_bezirk": "Schleswig",
        "version": "2025.1",
        "gueltig_ab": date(2025, 1, 1),
        "parameter": {
            # Berufsbedingte Aufwendungen
            "berufsbedingte_aufwendungen": {
                "pauschal_prozent": 0.05,
                "minimum": 50,
                "maximum": 150,
                "bei_selbstaendigen": "tatsaechliche_kosten"
            },

            # Altersvorsorge
            "altersvorsorge": {
                "zusaetzlich_prozent_brutto": 0.04,
                "begruendung": "4% des Bruttoeinkommens als zusaetzliche Altersvorsorge"
            },

            # Erwerbstaetigenbonus (Ehegattenunterhalt)
            "erwerbstaetigenbonus": {
                "quote": 1/7,  # ca. 14,3%
                "methode": "differenzmethode",
                "anwendung": "bei_einseitigem_erwerbseinkommen"
            },

            # Selbstbehalte
            "selbstbehalt": {
                # Gegenueber minderjaehrigen und privilegiert volljaehrigen Kindern
                "minderjaehrig_erwerbstaetig": 1450,
                "minderjaehrig_nicht_erwerbstaetig": 1200,

                # Gegenueber volljaehrigen Kindern
                "volljaehrig": 1750,

                # Gegenueber Ehegatten
                "ehegatte_erwerbstaetig": 1600,
                "ehegatte_nicht_erwerbstaetig": 1475,

                # Gegenueber Eltern
                "eltern": 2650,
            },

            # Wohnvorteil
            "wohnvorteil": {
                "methode": "objektiver_mietwert",
                "abzug_belastungen": True,
                "begruendung": "Objektiver Mietwert abzueglich Zins und Tilgung"
            },

            # Selbstaendige
            "selbstaendige": {
                "durchschnitt_jahre": 3,
                "basis": "gewinn_nach_steuern",
                "begruendung": "Durchschnitt der letzten 3 Jahre"
            },

            # Mangelfallberechnung
            "mangelfall": {
                "methode": "quotenmethode",
                "vorrang_minderjaehrige": True,
                "berechnungsweise": "anteilig_nach_bedarf"
            },

            # Herabstufung bei mehreren Berechtigten
            "herabstufung": {
                "ab_anzahl": 4,
                "stufen": 1,
                "begruendung": "Ab 4 Unterhaltsberechtigten Herabstufung um eine Stufe"
            }
        }
    }

    # Weitere OLG-Regelwerke (Auswahl)
    OLG_REGELWERKE = {
        "Schleswig": OLG_SCHLESWIG_2025,
        # Weitere OLGs koennen hier ergaenzt werden
    }

    @classmethod
    def get_duesseldorfer_tabelle(cls, stichtag: Optional[date] = None) -> Dict:
        """Gibt die Duesseldorfer Tabelle fuer einen Stichtag zurueck"""
        # Aktuell nur 2025 implementiert
        return cls.DUESSELDORFER_TABELLE_2025

    @classmethod
    def get_einkommensgruppe(cls, nettoeinkommen: float, stichtag: Optional[date] = None) -> int:
        """Ermittelt die Einkommensgruppe nach Duesseldorfer Tabelle"""
        dt = cls.get_duesseldorfer_tabelle(stichtag)

        for gruppe, (von, bis) in dt["einkommensgruppen"].items():
            if von <= nettoeinkommen <= bis:
                return gruppe

        # Ueber hoechster Gruppe
        if nettoeinkommen > 11200:
            return 15  # Hoechste Gruppe, darueberhinaus einzelfallabhaengig

        return 1  # Unter niedrigster Gruppe

    @classmethod
    def get_tabellenbetrag(
        cls,
        einkommensgruppe: int,
        altersstufe: int,
        stichtag: Optional[date] = None
    ) -> int:
        """Gibt den Tabellenbetrag fuer Einkommensgruppe und Altersstufe zurueck"""
        dt = cls.get_duesseldorfer_tabelle(stichtag)
        return dt["betraege"].get(einkommensgruppe, {}).get(altersstufe, 0)

    @classmethod
    def get_kindergeld(cls, stichtag: Optional[date] = None) -> int:
        """Gibt den aktuellen Kindergeldbetrag zurueck"""
        dt = cls.get_duesseldorfer_tabelle(stichtag)
        return dt["kindergeld"]

    @classmethod
    def get_ruleset(cls, olg_bezirk: str) -> RulesetInfo:
        """Gibt das Regelwerk fuer einen OLG-Bezirk zurueck"""
        ruleset_data = cls.OLG_REGELWERKE.get(olg_bezirk)

        if not ruleset_data:
            # Fallback auf Schleswig
            ruleset_data = cls.OLG_SCHLESWIG_2025

        return RulesetInfo(
            olg_bezirk=ruleset_data["olg_bezirk"],
            version=ruleset_data["version"],
            gueltig_ab=ruleset_data["gueltig_ab"],
            parameter=ruleset_data["parameter"]
        )

    @classmethod
    def get_selbstbehalt(
        cls,
        olg_bezirk: str,
        gegenueber: str,
        erwerbstaetig: bool = True
    ) -> int:
        """Ermittelt den Selbstbehalt nach OLG-Leitlinien"""
        ruleset = cls.get_ruleset(olg_bezirk)
        sb = ruleset.parameter.get("selbstbehalt", {})

        if gegenueber == "minderjaehrig":
            if erwerbstaetig:
                return sb.get("minderjaehrig_erwerbstaetig", 1450)
            else:
                return sb.get("minderjaehrig_nicht_erwerbstaetig", 1200)
        elif gegenueber == "volljaehrig":
            return sb.get("volljaehrig", 1750)
        elif gegenueber == "ehegatte":
            if erwerbstaetig:
                return sb.get("ehegatte_erwerbstaetig", 1600)
            else:
                return sb.get("ehegatte_nicht_erwerbstaetig", 1475)
        elif gegenueber == "eltern":
            return sb.get("eltern", 2650)

        return 1450  # Fallback

    @classmethod
    def get_berufsbedingte_aufwendungen(
        cls,
        nettoeinkommen: float,
        olg_bezirk: str,
        tatsaechliche_kosten: Optional[float] = None
    ) -> float:
        """Berechnet die berufsbedingten Aufwendungen"""
        ruleset = cls.get_ruleset(olg_bezirk)
        params = ruleset.parameter.get("berufsbedingte_aufwendungen", {})

        # Pauschale
        prozent = params.get("pauschal_prozent", 0.05)
        minimum = params.get("minimum", 50)
        maximum = params.get("maximum", 150)

        pauschale = nettoeinkommen * prozent
        pauschale = max(minimum, min(maximum, pauschale))

        # Tatsaechliche Kosten wenn hoeher und nachgewiesen
        if tatsaechliche_kosten and tatsaechliche_kosten > pauschale:
            return tatsaechliche_kosten

        return pauschale

    @classmethod
    def get_erwerbstaetigenbonus(cls, olg_bezirk: str) -> float:
        """Gibt die Erwerbstaetigenbonus-Quote zurueck"""
        ruleset = cls.get_ruleset(olg_bezirk)
        bonus_params = ruleset.parameter.get("erwerbstaetigenbonus", {})
        return bonus_params.get("quote", 1/7)

    @classmethod
    def bestimme_olg_bezirk(cls, plz: str = None, ort: str = None, gericht: str = None) -> str:
        """
        Bestimmt den zustaendigen OLG-Bezirk anhand von PLZ, Ort oder Gericht.
        Vereinfachte Implementierung fuer Schleswig-Holstein.
        """
        # PLZ-Bereiche Schleswig-Holstein: 22000-25999
        if plz:
            plz_int = int(plz[:2]) if plz else 0
            if 22 <= plz_int <= 25:
                return "Schleswig"

        # Orte in Schleswig-Holstein
        sh_orte = [
            "kiel", "luebeck", "flensburg", "neumuenster", "rendsburg",
            "eckernfoerde", "husum", "heide", "schleswig", "pinneberg",
            "elmshorn", "itzehoe", "norderstedt", "ahrensburg"
        ]

        if ort and ort.lower() in sh_orte:
            return "Schleswig"

        # Gerichte mit "Schleswig" oder SH-Staedten
        if gericht:
            gericht_lower = gericht.lower()
            if "schleswig" in gericht_lower:
                return "Schleswig"
            for sh_ort in sh_orte:
                if sh_ort in gericht_lower:
                    return "Schleswig"

        # Fallback
        return "Schleswig"

    @classmethod
    def get_verfuegbare_bezirke(cls) -> List[str]:
        """Gibt alle verfuegbaren OLG-Bezirke zurueck"""
        return list(cls.OLG_REGELWERKE.keys())
