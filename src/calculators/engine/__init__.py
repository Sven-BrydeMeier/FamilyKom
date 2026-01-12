"""
FamilyKom Calculation Engine
============================

Rechenkern fuer familienrechtliche Berechnungen nach
Duesseldorfer Tabelle und OLG-Leitlinien.

Alle Berechnungen sind deterministisch, versioniert und
liefern neben dem Ergebnis auch Zwischenschritte.
"""

from .base import CalculationResult, CalculationStep, RulesetInfo
from .kindesunterhalt import KindesunterhaltCalculator
from .ehegattenunterhalt import EhegattenunterhaltCalculator
from .zugewinn import ZugewinnCalculator
from .rvg import RVGCalculator
from .ruleset import RulesetManager

__all__ = [
    'CalculationResult',
    'CalculationStep',
    'RulesetInfo',
    'KindesunterhaltCalculator',
    'EhegattenunterhaltCalculator',
    'ZugewinnCalculator',
    'RVGCalculator',
    'RulesetManager',
]

__version__ = '1.0.0'
