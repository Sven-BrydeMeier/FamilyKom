"""
Datenmodule fuer FamilyKom

Enthaelt:
- Gerichtsdatenbank (gerichte.py)
"""

from .gerichte import (
    AMTSGERICHTE,
    OBERLANDESGERICHTE,
    JUGENDAEMTER,
    get_zustaendiges_gericht,
    get_zustaendiges_jugendamt,
    get_alle_amtsgerichte,
    get_alle_oberlandesgerichte,
    get_alle_jugendaemter,
    suche_gericht,
)
