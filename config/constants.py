"""
Konstanten für die Familienrechts-Applikation

Enthält:
- Düsseldorfer Tabelle 2025
- Selbstbehaltssätze
- RVG-Gebührentabelle
- OLG-Leitlinien Schleswig-Holstein
- Kindergeld-Sätze
- VPI-Referenzwerte
"""

from enum import Enum
from typing import Dict, List, Tuple

# =============================================================================
# DÜSSELDORFER TABELLE 2025
# =============================================================================

# Einkommensgrenzen je Gruppe (Obergrenze in Euro)
EINKOMMENSGRUPPEN_2025: Dict[int, Tuple[int, int]] = {
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
}

# Düsseldorfer Tabelle 2025: [Gruppe][Altersstufe] = Betrag in Euro
# Altersstufen: 0 = 0-5 Jahre, 1 = 6-11 Jahre, 2 = 12-17 Jahre, 3 = ab 18 Jahre
DUESSELDORFER_TABELLE_2025: Dict[int, Dict[int, int]] = {
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
}

# Prozentsätze je Gruppe (Gruppe 1 = 100%)
PROZENTSAETZE_GRUPPEN: Dict[int, int] = {
    1: 100, 2: 105, 3: 110, 4: 115, 5: 120,
    6: 128, 7: 136, 8: 144, 9: 152, 10: 160,
    11: 168, 12: 176, 13: 184, 14: 192, 15: 200,
}

# =============================================================================
# SELBSTBEHALT 2025
# =============================================================================

class SelbstbehaltTyp(Enum):
    """Arten des Selbstbehalts"""
    MINDERJAEHRIG_ERWERBSTAETIG = "minderjaehrig_erwerbstaetig"
    MINDERJAEHRIG_NICHT_ERWERBSTAETIG = "minderjaehrig_nicht_erwerbstaetig"
    VOLLJAEHRIG = "volljaehrig"
    EHEGATTE_ERWERBSTAETIG = "ehegatte_erwerbstaetig"
    EHEGATTE_NICHT_ERWERBSTAETIG = "ehegatte_nicht_erwerbstaetig"
    ELTERN = "eltern"


SELBSTBEHALT_2025: Dict[SelbstbehaltTyp, int] = {
    SelbstbehaltTyp.MINDERJAEHRIG_ERWERBSTAETIG: 1450,
    SelbstbehaltTyp.MINDERJAEHRIG_NICHT_ERWERBSTAETIG: 1200,
    SelbstbehaltTyp.VOLLJAEHRIG: 1750,
    SelbstbehaltTyp.EHEGATTE_ERWERBSTAETIG: 1600,
    SelbstbehaltTyp.EHEGATTE_NICHT_ERWERBSTAETIG: 1475,
    SelbstbehaltTyp.ELTERN: 2650,
}

# Bedarfskontrollbeträge 2025
BEDARFSKONTROLLBETRAEGE_2025: Dict[int, int] = {
    1: 1200,
    2: 1500,
    3: 1600,
    4: 1700,
    5: 1800,
    6: 1900,
    7: 2000,
    8: 2100,
    9: 2200,
    10: 2300,
    11: 2400,
    12: 2500,
    13: 2600,
    14: 2700,
    15: 2800,
}

# =============================================================================
# KINDERGELD 2025
# =============================================================================

KINDERGELD_2025: int = 255  # Euro pro Kind pro Monat
KINDERGELD_HALB_2025: float = 127.50  # Hälftiger Abzug bei Minderjährigen

# =============================================================================
# RVG GEBÜHRENTABELLE (Stand 01.06.2025)
# =============================================================================

# Gegenstandswert -> Einfache Gebühr (§ 13 RVG)
RVG_TABELLE_2025: List[Tuple[int, float]] = [
    (500, 51.50),
    (1000, 93.00),
    (1500, 124.00),
    (2000, 176.00),
    (3000, 235.50),
    (4000, 295.00),
    (5000, 354.50),
    (6000, 414.00),
    (7000, 473.50),
    (8000, 533.00),
    (9000, 592.50),
    (10000, 652.00),
    (13000, 772.50),
    (16000, 893.00),
    (19000, 1013.50),
    (22000, 1134.00),
    (25000, 1182.00),
    (30000, 1315.00),
    (35000, 1448.00),
    (40000, 1581.00),
    (45000, 1714.00),
    (50000, 1888.00),
    (65000, 2178.00),
    (80000, 2468.00),
    (95000, 2758.00),
    (110000, 3048.00),
    (125000, 3338.00),
    (140000, 3628.00),
    (155000, 3918.00),
    (170000, 4208.00),
    (185000, 4498.00),
    (200000, 4788.00),
    (230000, 5112.00),
    (260000, 5436.00),
    (290000, 5760.00),
    (320000, 6084.00),
    (350000, 6408.00),
    (380000, 6732.00),
    (410000, 7056.00),
    (440000, 7380.00),
    (470000, 7704.00),
    (500000, 8028.00),
]

# Gebührensätze
RVG_GEBUEHRENSAETZE: Dict[str, float] = {
    "geschaeftsgebuehr_normal": 1.3,
    "geschaeftsgebuehr_umfangreich": 2.5,
    "verfahrensgebuehr": 1.3,
    "terminsgebuehr": 1.2,
    "einigungsgebuehr": 1.5,
    "einigungsgebuehr_gericht": 1.0,
    "beratungsgebuehr_erstberatung": 0.0,  # Pauschal 190€
    "beratungsgebuehr_weitere": 0.0,  # Pauschal 250€
}

# Pauschalen
RVG_PAUSCHALEN: Dict[str, float] = {
    "erstberatung_verbraucher": 190.00,
    "weitere_beratung": 250.00,
    "auslagenpauschale_prozent": 0.20,  # 20% der Gebühren
    "auslagenpauschale_max": 20.00,
    "post_telekom_pauschale": 20.00,
    "dokumentenpauschale_seite": 0.50,
    "dokumentenpauschale_ab_51": 0.15,
}

# =============================================================================
# GEGENSTANDSWERTE FAMILIENRECHT (FamGKG)
# =============================================================================

GEGENSTANDSWERTE_FAMGKG: Dict[str, Dict] = {
    "ehescheidung": {
        "berechnung": "3-faches Nettoeinkommen beider Eheleute",
        "minimum": 3000,
        "maximum": None,
    },
    "versorgungsausgleich": {
        "berechnung": "10% des Ehescheidungswerts je Anrecht",
        "minimum": 1000,
        "je_anrecht": True,
    },
    "kindschaftssachen": {
        "wert": 5000,  # ab 01.06.2025
    },
    "ehewohnung_haushalt": {
        "wert": 4000,  # ab 01.06.2025
    },
    "unterhalt": {
        "berechnung": "12-facher Jahresbetrag",
    },
    "zugewinn": {
        "berechnung": "Höhe der Ausgleichsforderung",
    },
}

# =============================================================================
# OLG-BEZIRKE UND LEITLINIEN
# =============================================================================

class OLGBezirk(Enum):
    """Oberlandesgerichtsbezirke"""
    BAMBERG = "Bamberg"
    BERLIN = "Berlin"
    BRAUNSCHWEIG = "Braunschweig"
    BREMEN = "Bremen"
    CELLE = "Celle"
    DRESDEN = "Dresden"
    DUESSELDORF = "Düsseldorf"
    FRANKFURT = "Frankfurt am Main"
    HAMBURG = "Hamburg"
    HAMM = "Hamm"
    JENA = "Jena"
    KARLSRUHE = "Karlsruhe"
    KOBLENZ = "Koblenz"
    KOELN = "Köln"
    MUENCHEN = "München"
    NAUMBURG = "Naumburg"
    NUERNBERG = "Nürnberg"
    OLDENBURG = "Oldenburg"
    ROSTOCK = "Rostock"
    SAARBRUECKEN = "Saarbrücken"
    SCHLESWIG = "Schleswig"
    STUTTGART = "Stuttgart"
    ZWEIBRUECKEN = "Zweibrücken"


# Postleitzahl-Bereiche für OLG Schleswig-Holstein
PLZ_OLG_SCHLESWIG: List[str] = [
    "20", "21", "22", "23", "24", "25",  # Hamburg-Bereich, Schleswig-Holstein
]

# OLG Schleswig-Holstein Leitlinien 2025 - Besonderheiten
OLG_SCHLESWIG_LEITLINIEN_2025: Dict[str, any] = {
    "berufsbedingte_aufwendungen_pauschal": 0.05,  # 5%
    "berufsbedingte_aufwendungen_min": 50,
    "berufsbedingte_aufwendungen_max": 150,
    "altersvorsorge_prozent": 0.04,  # 4% des Bruttoeinkommens
    "erwerbstaetigenbonus": 0.10,  # 1/10 des bereinigten Erwerbseinkommens
    "selbstaendige_durchschnitt_jahre": 3,
    "wohnvorteil": "objektiver_mietwert_abzgl_belastungen",
}

# =============================================================================
# UNTERHALTSARTEN
# =============================================================================

class Unterhaltsart(Enum):
    """Arten des Unterhalts"""
    KINDESUNTERHALT = "kindesunterhalt"
    TRENNUNGSUNTERHALT = "trennungsunterhalt"
    NACHEHELICHER_UNTERHALT = "nachehelicher_unterhalt"
    ELTERNUNTERHALT = "elternunterhalt"


class NachehelicheUnterhaltstatbestaende(Enum):
    """Unterhaltstatbestände nach §§ 1570 ff. BGB"""
    BETREUUNGSUNTERHALT = ("§ 1570 BGB", "Betreuung gemeinsamer Kinder")
    ALTERSUNTERHALT = ("§ 1571 BGB", "Alter bei Scheidung/Ende Kindesbetreuung")
    KRANKHEITSUNTERHALT = ("§ 1572 BGB", "Krankheit oder Gebrechen")
    ERWERBSLOSIGKEITSUNTERHALT = ("§ 1573 Abs. 1 BGB", "Keine angemessene Erwerbstätigkeit")
    AUFSTOCKUNGSUNTERHALT = ("§ 1573 Abs. 2 BGB", "Einkünfte nicht ausreichend")
    AUSBILDUNGSUNTERHALT = ("§ 1574 BGB", "Ausbildung/Fortbildung")
    BILLIGKEITSUNTERHALT = ("§ 1576 BGB", "Schwerwiegende Gründe")

# =============================================================================
# VERBRAUCHERPREISINDEX (VPI) - Referenzwerte
# =============================================================================

# Basis: 2020 = 100
VPI_REFERENZWERTE: Dict[int, float] = {
    2015: 93.0,
    2016: 93.5,
    2017: 95.0,
    2018: 96.7,
    2019: 98.1,
    2020: 100.0,
    2021: 103.1,
    2022: 110.4,
    2023: 117.4,
    2024: 120.2,
    2025: 122.5,  # Geschätzt
}

# =============================================================================
# FALLTYPEN
# =============================================================================

class Falltyp(Enum):
    """Arten von Familiensachen"""
    KINDESUNTERHALT = "kindesunterhalt"
    TRENNUNGSUNTERHALT = "trennungsunterhalt"
    NACHEHELICHER_UNTERHALT = "nachehelicher_unterhalt"
    SCHEIDUNG = "scheidung"
    ZUGEWINNAUSGLEICH = "zugewinnausgleich"
    SORGERECHT = "sorgerecht"
    UMGANGSRECHT = "umgangsrecht"
    VERSORGUNGSAUSGLEICH = "versorgungsausgleich"


# =============================================================================
# DOKUMENTENTYPEN
# =============================================================================

class Dokumenttyp(Enum):
    """Typen von Dokumenten im Mandat"""
    ENTGELTABRECHNUNG = "entgeltabrechnung"
    STEUERBESCHEID = "steuerbescheid"
    KONTOAUSZUG = "kontoauszug"
    GEBURTSURKUNDE = "geburtsurkunde"
    HEIRATSURKUNDE = "heiratsurkunde"
    GRUNDBUCHAUSZUG = "grundbuchauszug"
    MIETVERTRAG = "mietvertrag"
    ARBEITSVERTRAG = "arbeitsvertrag"
    SCHRIFTSATZ = "schriftsatz"
    BESCHLUSS = "beschluss"
    URTEIL = "urteil"
    VOLLMACHT = "vollmacht"
    SONSTIGES = "sonstiges"


# =============================================================================
# BENUTZERROLLEN
# =============================================================================

class Benutzerrolle(Enum):
    """Rollen im System"""
    ADMIN = "admin"
    ANWALT = "anwalt"
    MITARBEITER = "mitarbeiter"
    MANDANT = "mandant"
