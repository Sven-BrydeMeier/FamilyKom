"""
Kindesunterhalt-Berechnung nach Düsseldorfer Tabelle

Implementiert die Berechnungslogik gemäß:
- Düsseldorfer Tabelle 2025
- OLG-Leitlinien Schleswig-Holstein
- § 1612a BGB (Mindestunterhalt)
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict, Any

from config.constants import (
    DUESSELDORFER_TABELLE_2025,
    EINKOMMENSGRUPPEN_2025,
    SELBSTBEHALT_2025,
    SelbstbehaltTyp,
    KINDERGELD_2025,
    KINDERGELD_HALB_2025,
    BEDARFSKONTROLLBETRAEGE_2025,
    OLG_SCHLESWIG_LEITLINIEN_2025,
)


@dataclass
class Kind:
    """Datenklasse für ein unterhaltsberechtigtes Kind"""
    name: str
    geburtsdatum: date
    lebt_bei_pflichtigem: bool = False
    eigenes_einkommen: float = 0.0
    privilegiert: bool = True  # § 1603 Abs. 2 BGB

    @property
    def alter(self) -> int:
        """Berechnet das aktuelle Alter des Kindes"""
        heute = date.today()
        alter = heute.year - self.geburtsdatum.year
        if (heute.month, heute.day) < (self.geburtsdatum.month, self.geburtsdatum.day):
            alter -= 1
        return alter

    @property
    def altersstufe(self) -> int:
        """Bestimmt die Altersstufe nach Düsseldorfer Tabelle"""
        alter = self.alter
        if alter <= 5:
            return 0
        elif alter <= 11:
            return 1
        elif alter <= 17:
            return 2
        else:
            return 3

    @property
    def ist_minderjaehrig(self) -> bool:
        """Prüft, ob das Kind minderjährig ist"""
        return self.alter < 18


@dataclass
class Einkommensbereinigung:
    """Datenklasse für die Einkommensbereinigung"""
    bruttoeinkommen: float
    nettoeinkommen: float
    berufsbedingte_aufwendungen: Optional[float] = None
    fahrtkosten: float = 0.0
    fortbildungskosten: float = 0.0
    gewerkschaftsbeitraege: float = 0.0
    private_altersvorsorge: float = 0.0  # max 4% vom Brutto
    schulden: float = 0.0
    vorrangige_unterhaltslasten: float = 0.0

    def berechne_bereinigte_aufwendungen(self) -> float:
        """
        Berechnet berufsbedingte Aufwendungen
        Pauschal: 5% des Netto, mind. 50€, max. 150€
        Oder: Tatsächliche Kosten bei Nachweis
        """
        if self.berufsbedingte_aufwendungen is not None:
            return self.berufsbedingte_aufwendungen

        pauschal = self.nettoeinkommen * OLG_SCHLESWIG_LEITLINIEN_2025["berufsbedingte_aufwendungen_pauschal"]
        return max(
            OLG_SCHLESWIG_LEITLINIEN_2025["berufsbedingte_aufwendungen_min"],
            min(pauschal, OLG_SCHLESWIG_LEITLINIEN_2025["berufsbedingte_aufwendungen_max"])
        )

    def berechne_zulaessige_altersvorsorge(self) -> float:
        """Berechnet die abzugsfähige private Altersvorsorge (max 4% Brutto)"""
        max_vorsorge = self.bruttoeinkommen * OLG_SCHLESWIG_LEITLINIEN_2025["altersvorsorge_prozent"]
        return min(self.private_altersvorsorge, max_vorsorge)

    def berechne_bereinigtes_netto(self) -> float:
        """Berechnet das bereinigte Nettoeinkommen"""
        bereinigt = self.nettoeinkommen
        bereinigt -= self.berechne_bereinigte_aufwendungen()
        bereinigt -= self.fahrtkosten
        bereinigt -= self.fortbildungskosten
        bereinigt -= self.gewerkschaftsbeitraege
        bereinigt -= self.berechne_zulaessige_altersvorsorge()
        bereinigt -= self.schulden
        bereinigt -= self.vorrangige_unterhaltslasten
        return max(0, bereinigt)


@dataclass
class KindesunterhaltErgebnis:
    """Ergebnis der Kindesunterhalt-Berechnung"""
    kind_name: str
    alter: int
    altersstufe: int
    einkommensgruppe: int
    angepasste_gruppe: int
    tabellenbetrag: float
    kindergeldabzug: float
    zahlbetrag: float
    selbstbehalt_unterschritten: bool = False
    mangelfall: bool = False
    hinweise: List[str] = field(default_factory=list)


@dataclass
class GesamtErgebnis:
    """Gesamtergebnis für alle Kinder"""
    bereinigtes_einkommen: float
    einkommensgruppe: int
    anzahl_unterhaltsberechtigte: int
    gruppenanpassung: int
    kinder_ergebnisse: List[KindesunterhaltErgebnis]
    gesamtunterhalt: float
    verbleibendes_einkommen: float
    selbstbehalt: float
    ist_mangelfall: bool = False
    berechnungsdetails: Dict[str, Any] = field(default_factory=dict)


class KindesunterhaltRechner:
    """
    Rechner für Kindesunterhalt nach Düsseldorfer Tabelle

    Berücksichtigt:
    - Einkommensbereinigung nach OLG-Leitlinien
    - Gruppenauf-/abstufung bei Anzahl Unterhaltsberechtigter
    - Kindergeldanrechnung
    - Selbstbehaltsprüfung
    - Mangelfallberechnung
    """

    def __init__(
        self,
        tabelle: Dict[int, Dict[int, int]] = None,
        einkommensgruppen: Dict[int, tuple] = None
    ):
        self.tabelle = tabelle or DUESSELDORFER_TABELLE_2025
        self.einkommensgruppen = einkommensgruppen or EINKOMMENSGRUPPEN_2025

    def ermittle_einkommensgruppe(self, bereinigtes_netto: float) -> int:
        """
        Ermittelt die Einkommensgruppe basierend auf dem bereinigten Nettoeinkommen
        """
        for gruppe, (untergrenze, obergrenze) in self.einkommensgruppen.items():
            if untergrenze <= bereinigtes_netto <= obergrenze:
                return gruppe

        # Über höchster Gruppe
        if bereinigtes_netto > 11200:
            return 15

        # Unter niedrigster Gruppe
        return 1

    def passe_gruppe_an(self, gruppe: int, anzahl_berechtigte: int) -> int:
        """
        Passt die Einkommensgruppe an die Anzahl der Unterhaltsberechtigten an

        - Bei 1 Berechtigtem: +1 Gruppe
        - Bei 2 Berechtigten: keine Anpassung (Standardfall)
        - Bei 3+ Berechtigten: -1 Gruppe je weiterem Berechtigten
        """
        if anzahl_berechtigte == 1:
            anpassung = 1
        elif anzahl_berechtigte == 2:
            anpassung = 0
        else:
            anpassung = -(anzahl_berechtigte - 2)

        neue_gruppe = gruppe + anpassung
        return max(1, min(neue_gruppe, 15))

    def hole_tabellenbetrag(self, gruppe: int, altersstufe: int) -> float:
        """Holt den Tabellenbetrag aus der Düsseldorfer Tabelle"""
        if gruppe in self.tabelle and altersstufe in self.tabelle[gruppe]:
            return float(self.tabelle[gruppe][altersstufe])
        return 0.0

    def berechne_kindergeldabzug(self, ist_minderjaehrig: bool) -> float:
        """
        Berechnet den Kindergeldabzug

        - Minderjährige: Hälftiges Kindergeld
        - Volljährige: Volles Kindergeld
        """
        if ist_minderjaehrig:
            return KINDERGELD_HALB_2025
        return float(KINDERGELD_2025)

    def ermittle_selbstbehalt(
        self,
        erwerbstaetig: bool,
        kind_minderjaehrig: bool,
        kind_privilegiert: bool = True
    ) -> float:
        """Ermittelt den anwendbaren Selbstbehalt"""
        if kind_minderjaehrig or kind_privilegiert:
            if erwerbstaetig:
                return float(SELBSTBEHALT_2025[SelbstbehaltTyp.MINDERJAEHRIG_ERWERBSTAETIG])
            return float(SELBSTBEHALT_2025[SelbstbehaltTyp.MINDERJAEHRIG_NICHT_ERWERBSTAETIG])
        return float(SELBSTBEHALT_2025[SelbstbehaltTyp.VOLLJAEHRIG])

    def pruefe_bedarfskontrolle(self, gruppe: int, verbleibendes_einkommen: float) -> bool:
        """
        Prüft, ob der Bedarfskontrollbetrag unterschritten wird
        """
        kontrollbetrag = BEDARFSKONTROLLBETRAEGE_2025.get(gruppe, 1200)
        return verbleibendes_einkommen >= kontrollbetrag

    def berechne_mangelfall(
        self,
        bereinigtes_einkommen: float,
        selbstbehalt: float,
        kinder: List[Kind]
    ) -> Dict[str, float]:
        """
        Berechnet die Verteilung im Mangelfall

        Verteilungsmasse = Bereinigtes Einkommen - Selbstbehalt
        Verteilung nach Prozentsätzen der Bedarfsbeträge
        """
        verteilungsmasse = max(0, bereinigtes_einkommen - selbstbehalt)

        if verteilungsmasse == 0:
            return {kind.name: 0.0 for kind in kinder}

        # Bedarfsbeträge ermitteln (Mindestunterhalt = Gruppe 1)
        bedarfe = {}
        gesamtbedarf = 0.0

        for kind in kinder:
            bedarf = self.hole_tabellenbetrag(1, kind.altersstufe)
            # Kindergeld abziehen für Zahlbetrag
            if kind.ist_minderjaehrig:
                bedarf -= KINDERGELD_HALB_2025
            else:
                bedarf -= KINDERGELD_2025
            bedarfe[kind.name] = max(0, bedarf)
            gesamtbedarf += bedarfe[kind.name]

        # Quoten berechnen und Verteilung
        verteilung = {}
        for kind in kinder:
            if gesamtbedarf > 0:
                quote = bedarfe[kind.name] / gesamtbedarf
                verteilung[kind.name] = round(verteilungsmasse * quote, 2)
            else:
                verteilung[kind.name] = 0.0

        return verteilung

    def berechne(
        self,
        einkommen: Einkommensbereinigung,
        kinder: List[Kind],
        erwerbstaetig: bool = True,
        weitere_unterhaltsberechtigte: int = 0
    ) -> GesamtErgebnis:
        """
        Hauptmethode zur Berechnung des Kindesunterhalts

        Args:
            einkommen: Einkommensbereinigung-Objekt mit allen Einkommensdaten
            kinder: Liste der unterhaltsberechtigten Kinder
            erwerbstaetig: Ob der Pflichtige erwerbstätig ist
            weitere_unterhaltsberechtigte: Anzahl weiterer Unterhaltsberechtigter (z.B. Ehegatte)

        Returns:
            GesamtErgebnis mit allen Berechnungsdetails
        """
        # 1. Bereinigtes Nettoeinkommen berechnen
        bereinigtes_netto = einkommen.berechne_bereinigtes_netto()

        # 2. Einkommensgruppe ermitteln
        grundgruppe = self.ermittle_einkommensgruppe(bereinigtes_netto)

        # 3. Anzahl der Unterhaltsberechtigten
        anzahl_berechtigte = len(kinder) + weitere_unterhaltsberechtigte

        # 4. Gruppenanpassung
        angepasste_gruppe = self.passe_gruppe_an(grundgruppe, anzahl_berechtigte)

        # 5. Selbstbehalt ermitteln (für minderjährige/privilegierte Kinder)
        hat_minderjaehrige = any(k.ist_minderjaehrig for k in kinder)
        hat_privilegierte = any(k.privilegiert for k in kinder)
        selbstbehalt = self.ermittle_selbstbehalt(
            erwerbstaetig,
            hat_minderjaehrige,
            hat_privilegierte
        )

        # 6. Unterhalt für jedes Kind berechnen
        kinder_ergebnisse = []
        gesamtunterhalt = 0.0

        for kind in kinder:
            tabellenbetrag = self.hole_tabellenbetrag(angepasste_gruppe, kind.altersstufe)
            kindergeldabzug = self.berechne_kindergeldabzug(kind.ist_minderjaehrig)
            zahlbetrag = tabellenbetrag - kindergeldabzug

            # Eigenes Einkommen des Kindes berücksichtigen (bei Volljährigen)
            if not kind.ist_minderjaehrig and kind.eigenes_einkommen > 0:
                # Anrechnung des bereinigten Einkommens abzüglich Freibetrag
                anrechenbares_einkommen = max(0, kind.eigenes_einkommen - 100)  # 100€ Freibetrag
                zahlbetrag = max(0, zahlbetrag - anrechenbares_einkommen)

            hinweise = []

            ergebnis = KindesunterhaltErgebnis(
                kind_name=kind.name,
                alter=kind.alter,
                altersstufe=kind.altersstufe,
                einkommensgruppe=grundgruppe,
                angepasste_gruppe=angepasste_gruppe,
                tabellenbetrag=tabellenbetrag,
                kindergeldabzug=kindergeldabzug,
                zahlbetrag=zahlbetrag,
                hinweise=hinweise
            )
            kinder_ergebnisse.append(ergebnis)
            gesamtunterhalt += zahlbetrag

        # 7. Selbstbehaltsprüfung
        verbleibendes_einkommen = bereinigtes_netto - gesamtunterhalt
        ist_mangelfall = verbleibendes_einkommen < selbstbehalt

        # 8. Bei Mangelfall: Neuberechnung
        if ist_mangelfall:
            mangelfall_verteilung = self.berechne_mangelfall(
                bereinigtes_netto,
                selbstbehalt,
                kinder
            )

            # Ergebnisse aktualisieren
            gesamtunterhalt = 0.0
            for ergebnis in kinder_ergebnisse:
                neuer_zahlbetrag = mangelfall_verteilung.get(ergebnis.kind_name, 0.0)
                ergebnis.zahlbetrag = neuer_zahlbetrag
                ergebnis.mangelfall = True
                ergebnis.hinweise.append(
                    f"Mangelfall: Zahlbetrag von {ergebnis.tabellenbetrag - ergebnis.kindergeldabzug:.2f}€ "
                    f"auf {neuer_zahlbetrag:.2f}€ reduziert"
                )
                gesamtunterhalt += neuer_zahlbetrag

            verbleibendes_einkommen = bereinigtes_netto - gesamtunterhalt

        # 9. Bedarfskontrolle prüfen
        if not self.pruefe_bedarfskontrolle(angepasste_gruppe, verbleibendes_einkommen):
            for ergebnis in kinder_ergebnisse:
                ergebnis.hinweise.append(
                    "Bedarfskontrollbetrag unterschritten - ggf. Herabstufung prüfen"
                )

        # 10. Berechnungsdetails zusammenstellen
        berechnungsdetails = {
            "bruttoeinkommen": einkommen.bruttoeinkommen,
            "nettoeinkommen": einkommen.nettoeinkommen,
            "berufsbedingte_aufwendungen": einkommen.berechne_bereinigte_aufwendungen(),
            "altersvorsorge": einkommen.berechne_zulaessige_altersvorsorge(),
            "weitere_abzuege": (
                einkommen.fahrtkosten +
                einkommen.fortbildungskosten +
                einkommen.gewerkschaftsbeitraege +
                einkommen.schulden +
                einkommen.vorrangige_unterhaltslasten
            ),
            "kindergeld": KINDERGELD_2025,
            "bedarfskontrollbetrag": BEDARFSKONTROLLBETRAEGE_2025.get(angepasste_gruppe, 1200),
        }

        return GesamtErgebnis(
            bereinigtes_einkommen=bereinigtes_netto,
            einkommensgruppe=grundgruppe,
            anzahl_unterhaltsberechtigte=anzahl_berechtigte,
            gruppenanpassung=angepasste_gruppe - grundgruppe,
            kinder_ergebnisse=kinder_ergebnisse,
            gesamtunterhalt=gesamtunterhalt,
            verbleibendes_einkommen=verbleibendes_einkommen,
            selbstbehalt=selbstbehalt,
            ist_mangelfall=ist_mangelfall,
            berechnungsdetails=berechnungsdetails
        )

    def formatiere_ergebnis(self, ergebnis: GesamtErgebnis) -> str:
        """Formatiert das Ergebnis als lesbaren Text"""
        lines = [
            "=" * 60,
            "KINDESUNTERHALT-BERECHNUNG",
            "=" * 60,
            "",
            f"Bereinigtes Nettoeinkommen: {ergebnis.bereinigtes_einkommen:,.2f} €",
            f"Einkommensgruppe: {ergebnis.einkommensgruppe}",
            f"Anzahl Unterhaltsberechtigte: {ergebnis.anzahl_unterhaltsberechtigte}",
            f"Gruppenanpassung: {ergebnis.gruppenanpassung:+d}",
            "",
            "-" * 60,
            "UNTERHALT JE KIND:",
            "-" * 60,
        ]

        for kind_ergebnis in ergebnis.kinder_ergebnisse:
            lines.extend([
                "",
                f"  {kind_ergebnis.kind_name} ({kind_ergebnis.alter} Jahre, Altersstufe {kind_ergebnis.altersstufe + 1}):",
                f"    Einkommensgruppe (angepasst): {kind_ergebnis.angepasste_gruppe}",
                f"    Tabellenbetrag:    {kind_ergebnis.tabellenbetrag:>8,.2f} €",
                f"    Kindergeldabzug:   {kind_ergebnis.kindergeldabzug:>8,.2f} €",
                f"    Zahlbetrag:        {kind_ergebnis.zahlbetrag:>8,.2f} €",
            ])
            if kind_ergebnis.hinweise:
                for hinweis in kind_ergebnis.hinweise:
                    lines.append(f"    ⚠ {hinweis}")

        lines.extend([
            "",
            "-" * 60,
            f"GESAMTUNTERHALT:         {ergebnis.gesamtunterhalt:>8,.2f} €",
            f"Verbleibendes Einkommen: {ergebnis.verbleibendes_einkommen:>8,.2f} €",
            f"Selbstbehalt:            {ergebnis.selbstbehalt:>8,.2f} €",
            "-" * 60,
        ])

        if ergebnis.ist_mangelfall:
            lines.append("")
            lines.append("⚠ MANGELFALL: Der Selbstbehalt kann nicht gewahrt werden.")
            lines.append("  Die Zahlbeträge wurden entsprechend angepasst.")

        lines.append("=" * 60)

        return "\n".join(lines)
