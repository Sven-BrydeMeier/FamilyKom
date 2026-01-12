"""
Tests für die Kindesunterhalt-Berechnung
"""

import pytest
from datetime import date

from src.calculators.kindesunterhalt import (
    KindesunterhaltRechner,
    Kind,
    Einkommensbereinigung,
)


class TestKindesunterhaltRechner:
    """Tests für den Kindesunterhalt-Rechner"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.rechner = KindesunterhaltRechner()

    def test_ermittle_einkommensgruppe(self):
        """Test Einkommensgruppen-Ermittlung"""
        assert self.rechner.ermittle_einkommensgruppe(2000) == 1
        assert self.rechner.ermittle_einkommensgruppe(2100) == 1
        assert self.rechner.ermittle_einkommensgruppe(2500) == 2
        assert self.rechner.ermittle_einkommensgruppe(3500) == 5
        assert self.rechner.ermittle_einkommensgruppe(5000) == 9

    def test_passe_gruppe_an(self):
        """Test Gruppenanpassung bei unterschiedlicher Kinderzahl"""
        # 1 Kind: +1 Gruppe
        assert self.rechner.passe_gruppe_an(5, 1) == 6
        # 2 Kinder: keine Anpassung
        assert self.rechner.passe_gruppe_an(5, 2) == 5
        # 3 Kinder: -1 Gruppe
        assert self.rechner.passe_gruppe_an(5, 3) == 4
        # Minimum ist Gruppe 1
        assert self.rechner.passe_gruppe_an(1, 5) == 1

    def test_hole_tabellenbetrag(self):
        """Test Tabellenbetrag-Abfrage"""
        # Gruppe 1, Altersstufe 0 (0-5 Jahre)
        assert self.rechner.hole_tabellenbetrag(1, 0) == 482.0
        # Gruppe 5, Altersstufe 2 (12-17 Jahre)
        assert self.rechner.hole_tabellenbetrag(5, 2) == 779.0

    def test_berechne_kindergeldabzug(self):
        """Test Kindergeldabzug"""
        # Minderjährig: hälftiges Kindergeld
        assert self.rechner.berechne_kindergeldabzug(True) == 127.50
        # Volljährig: volles Kindergeld
        assert self.rechner.berechne_kindergeldabzug(False) == 255.0

    def test_kind_altersstufe(self):
        """Test Altersstufen-Berechnung"""
        # 3 Jahre alt -> Stufe 0
        kind = Kind(name="Test", geburtsdatum=date(2022, 1, 1))
        assert kind.altersstufe == 0

        # 8 Jahre alt -> Stufe 1
        kind = Kind(name="Test", geburtsdatum=date(2017, 1, 1))
        assert kind.altersstufe == 1

        # 15 Jahre alt -> Stufe 2
        kind = Kind(name="Test", geburtsdatum=date(2010, 1, 1))
        assert kind.altersstufe == 2

    def test_einkommensbereinigung(self):
        """Test Einkommensbereinigung"""
        einkommen = Einkommensbereinigung(
            bruttoeinkommen=5000,
            nettoeinkommen=3500,
            fahrtkosten=100,
            schulden=200
        )

        # Berufsbedingte Aufwendungen: 5% von 3500 = 175, max 150
        assert einkommen.berechne_bereinigte_aufwendungen() == 150

        # Bereinigtes Netto: 3500 - 150 - 100 - 200 = 3050
        assert einkommen.berechne_bereinigtes_netto() == 3050

    def test_vollstaendige_berechnung(self):
        """Test komplette Unterhaltsberechnung"""
        einkommen = Einkommensbereinigung(
            bruttoeinkommen=4500,
            nettoeinkommen=3200
        )

        kinder = [
            Kind(name="Anna", geburtsdatum=date(2018, 6, 15)),  # ca. 6 Jahre
        ]

        ergebnis = self.rechner.berechne(einkommen, kinder)

        # Prüfe dass Ergebnis plausibel ist
        assert ergebnis.bereinigtes_einkommen > 0
        assert ergebnis.gesamtunterhalt > 0
        assert len(ergebnis.kinder_ergebnisse) == 1
        assert not ergebnis.ist_mangelfall

    def test_mangelfall(self):
        """Test Mangelfallberechnung"""
        einkommen = Einkommensbereinigung(
            bruttoeinkommen=2000,
            nettoeinkommen=1600  # Sehr niedriges Einkommen
        )

        kinder = [
            Kind(name="Kind1", geburtsdatum=date(2018, 1, 1)),
            Kind(name="Kind2", geburtsdatum=date(2015, 1, 1)),
            Kind(name="Kind3", geburtsdatum=date(2012, 1, 1)),
        ]

        ergebnis = self.rechner.berechne(einkommen, kinder)

        # Bei sehr niedrigem Einkommen und 3 Kindern sollte Mangelfall vorliegen
        assert ergebnis.ist_mangelfall
        # Verbleibendes Einkommen sollte etwa Selbstbehalt sein
        assert ergebnis.verbleibendes_einkommen <= ergebnis.selbstbehalt + 50


class TestEinkommensbereinigung:
    """Tests für die Einkommensbereinigung"""

    def test_berufsbedingte_aufwendungen_minimum(self):
        """Test Minimum der berufsbedingten Aufwendungen"""
        einkommen = Einkommensbereinigung(
            bruttoeinkommen=1500,
            nettoeinkommen=800  # Sehr niedrig
        )
        # 5% von 800 = 40, aber Minimum ist 50
        assert einkommen.berechne_bereinigte_aufwendungen() == 50

    def test_berufsbedingte_aufwendungen_maximum(self):
        """Test Maximum der berufsbedingten Aufwendungen"""
        einkommen = Einkommensbereinigung(
            bruttoeinkommen=10000,
            nettoeinkommen=6000  # Hoch
        )
        # 5% von 6000 = 300, aber Maximum ist 150
        assert einkommen.berechne_bereinigte_aufwendungen() == 150

    def test_altersvorsorge_grenze(self):
        """Test Altersvorsorge-Grenze (4% vom Brutto)"""
        einkommen = Einkommensbereinigung(
            bruttoeinkommen=5000,
            nettoeinkommen=3500,
            private_altersvorsorge=300  # Mehr als 4% von 5000
        )
        # Max 4% von 5000 = 200
        assert einkommen.berechne_zulaessige_altersvorsorge() == 200
