"""
RVG-Gebührenrechner (Rechtsanwaltsvergütungsgesetz)

Stand: 01.06.2025 (nach KostBRÄG 2025)

Implementiert:
- Gebührenberechnung nach § 13 RVG
- Gegenstandswertberechnung im Familienrecht (FamGKG)
- Verschiedene Gebührenarten (Geschäfts-, Verfahrens-, Terminsgebühr)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Tuple

from config.constants import (
    RVG_TABELLE_2025,
    RVG_GEBUEHRENSAETZE,
    RVG_PAUSCHALEN,
    GEGENSTANDSWERTE_FAMGKG,
)


class Gebuehrenart(Enum):
    """Arten von RVG-Gebühren"""
    GESCHAEFTSGEBUEHR = "geschaeftsgebuehr"
    VERFAHRENSGEBUEHR = "verfahrensgebuehr"
    TERMINSGEBUEHR = "terminsgebuehr"
    EINIGUNGSGEBUEHR = "einigungsgebuehr"
    EINIGUNGSGEBUEHR_GERICHT = "einigungsgebuehr_gericht"
    BERATUNGSGEBUEHR = "beratungsgebuehr"


class Verfahrensart(Enum):
    """Verfahrensarten im Familienrecht"""
    EHESCHEIDUNG = "ehescheidung"
    VERSORGUNGSAUSGLEICH = "versorgungsausgleich"
    KINDSCHAFTSSACHE = "kindschaftssache"
    EHEWOHNUNG_HAUSHALT = "ehewohnung_haushalt"
    UNTERHALT = "unterhalt"
    ZUGEWINNAUSGLEICH = "zugewinnausgleich"


@dataclass
class Gebuehrenposition:
    """Eine einzelne Gebührenposition"""
    bezeichnung: str
    gebuehrenart: Gebuehrenart
    gegenstandswert: float
    gebuerensatz: float
    einfache_gebuehr: float
    gebuehr: float
    rechtsgrundlage: str = ""


@dataclass
class RVGErgebnis:
    """Ergebnis der RVG-Berechnung"""
    gegenstandswert: float
    positionen: List[Gebuehrenposition]
    summe_gebuehren: float
    auslagenpauschale: float
    mehrwertsteuer: float
    gesamtbetrag: float
    hinweise: List[str] = field(default_factory=list)
    berechnungsdetails: Dict[str, any] = field(default_factory=dict)


class RVGRechner:
    """
    Rechner für Rechtsanwaltsgebühren nach RVG

    Berechnet Gebühren basierend auf:
    - Gegenstandswert
    - Gebührenart und -satz
    - Auslagenpauschale
    - Mehrwertsteuer
    """

    def __init__(
        self,
        tabelle: List[Tuple[int, float]] = None,
        mwst_satz: float = 0.19
    ):
        self.tabelle = tabelle or RVG_TABELLE_2025
        self.mwst_satz = mwst_satz
        self.pauschalen = RVG_PAUSCHALEN
        self.saetze = RVG_GEBUEHRENSAETZE

    def ermittle_einfache_gebuehr(self, gegenstandswert: float) -> float:
        """
        Ermittelt die einfache Gebühr (1,0) aus der RVG-Tabelle

        Bei Werten über dem höchsten Tabellenwert wird linear interpoliert.
        """
        if gegenstandswert <= 0:
            return 0.0

        # Suche passenden Wert in der Tabelle
        vorherige_stufe = (0, 0.0)

        for wert, gebuehr in self.tabelle:
            if gegenstandswert <= wert:
                # Gefunden - Wert dieser Stufe verwenden
                return gebuehr
            vorherige_stufe = (wert, gebuehr)

        # Über höchstem Tabellenwert - lineare Fortschreibung
        # Ab 500.000€: je weitere 50.000€ kommen ca. 306€ hinzu
        hoechster_wert, hoechste_gebuehr = self.tabelle[-1]
        ueberschuss = gegenstandswert - hoechster_wert
        zusatz_stufen = ueberschuss / 50000
        zusatz_gebuehr = zusatz_stufen * 306.0  # Approximation

        return hoechste_gebuehr + zusatz_gebuehr

    def berechne_gebuehr(
        self,
        gegenstandswert: float,
        gebuerensatz: float
    ) -> Tuple[float, float]:
        """
        Berechnet eine Gebühr basierend auf Gegenstandswert und Satz

        Returns:
            Tuple aus (einfache_gebuehr, berechnete_gebuehr)
        """
        einfache = self.ermittle_einfache_gebuehr(gegenstandswert)
        gebuehr = einfache * gebuerensatz
        return einfache, round(gebuehr, 2)

    def berechne_gegenstandswert_ehescheidung(
        self,
        nettoeinkommen_a: float,
        nettoeinkommen_b: float
    ) -> float:
        """
        Berechnet den Gegenstandswert für die Ehescheidung nach § 43 FamGKG

        Formel: 3-faches Nettoeinkommen beider Eheleute
        Minimum: 3.000€
        """
        wert = (nettoeinkommen_a + nettoeinkommen_b) * 3
        minimum = GEGENSTANDSWERTE_FAMGKG["ehescheidung"]["minimum"]
        return max(wert, minimum)

    def berechne_gegenstandswert_versorgungsausgleich(
        self,
        gegenstandswert_scheidung: float,
        anzahl_anrechte: int
    ) -> float:
        """
        Berechnet den Gegenstandswert für den Versorgungsausgleich nach § 50 FamGKG

        Formel: 10% des Scheidungswerts je Anrecht, mind. 1.000€
        """
        wert_je_anrecht = gegenstandswert_scheidung * 0.10
        minimum = GEGENSTANDSWERTE_FAMGKG["versorgungsausgleich"]["minimum"]
        wert_je_anrecht = max(wert_je_anrecht, minimum)
        return wert_je_anrecht * anzahl_anrechte

    def berechne_gegenstandswert_unterhalt(
        self,
        monatlicher_unterhalt: float
    ) -> float:
        """
        Berechnet den Gegenstandswert für Unterhaltssachen nach § 51 FamGKG

        Formel: 12-facher Jahresbetrag
        """
        return monatlicher_unterhalt * 12

    def berechne_auslagenpauschale(self, summe_gebuehren: float) -> float:
        """
        Berechnet die Auslagenpauschale nach Nr. 7002 VV RVG

        20% der Gebühren, maximal 20€
        """
        pauschale = summe_gebuehren * self.pauschalen["auslagenpauschale_prozent"]
        return min(pauschale, self.pauschalen["auslagenpauschale_max"])

    def berechne_aussergericht(
        self,
        gegenstandswert: float,
        geschaeftsgebuehr_satz: float = 1.3,
        mit_einigung: bool = False
    ) -> RVGErgebnis:
        """
        Berechnet die außergerichtliche Vertretung

        Standard: 1,3 Geschäftsgebühr (Nr. 2300 VV RVG)
        Bei Einigung: Zusätzlich 1,5 Einigungsgebühr (Nr. 1000 VV RVG)
        """
        positionen = []
        hinweise = []

        # Geschäftsgebühr
        einfache, gebuehr = self.berechne_gebuehr(gegenstandswert, geschaeftsgebuehr_satz)
        positionen.append(Gebuehrenposition(
            bezeichnung="Geschäftsgebühr",
            gebuehrenart=Gebuehrenart.GESCHAEFTSGEBUEHR,
            gegenstandswert=gegenstandswert,
            gebuerensatz=geschaeftsgebuehr_satz,
            einfache_gebuehr=einfache,
            gebuehr=gebuehr,
            rechtsgrundlage="Nr. 2300 VV RVG"
        ))

        # Einigungsgebühr wenn zutreffend
        if mit_einigung:
            _, einigungsgebuehr = self.berechne_gebuehr(gegenstandswert, 1.5)
            positionen.append(Gebuehrenposition(
                bezeichnung="Einigungsgebühr",
                gebuehrenart=Gebuehrenart.EINIGUNGSGEBUEHR,
                gegenstandswert=gegenstandswert,
                gebuerensatz=1.5,
                einfache_gebuehr=einfache,
                gebuehr=einigungsgebuehr,
                rechtsgrundlage="Nr. 1000 VV RVG"
            ))

        summe = sum(p.gebuehr for p in positionen)
        auslagen = self.berechne_auslagenpauschale(summe)
        netto = summe + auslagen
        mwst = round(netto * self.mwst_satz, 2)
        gesamt = netto + mwst

        return RVGErgebnis(
            gegenstandswert=gegenstandswert,
            positionen=positionen,
            summe_gebuehren=summe,
            auslagenpauschale=auslagen,
            mehrwertsteuer=mwst,
            gesamtbetrag=gesamt,
            hinweise=hinweise
        )

    def berechne_gerichtlich(
        self,
        gegenstandswert: float,
        mit_termin: bool = True,
        mit_einigung: bool = False,
        verfahrensgebuehr_satz: float = 1.3,
        terminsgebuehr_satz: float = 1.2
    ) -> RVGErgebnis:
        """
        Berechnet die gerichtliche Vertretung

        - Verfahrensgebühr: 1,3 (Nr. 3100 VV RVG)
        - Terminsgebühr: 1,2 (Nr. 3104 VV RVG)
        - Einigungsgebühr: 1,0 bei Gericht (Nr. 1003 VV RVG)
        """
        positionen = []
        hinweise = []

        einfache = self.ermittle_einfache_gebuehr(gegenstandswert)

        # Verfahrensgebühr
        _, verfahrensgebuehr = self.berechne_gebuehr(gegenstandswert, verfahrensgebuehr_satz)
        positionen.append(Gebuehrenposition(
            bezeichnung="Verfahrensgebühr",
            gebuehrenart=Gebuehrenart.VERFAHRENSGEBUEHR,
            gegenstandswert=gegenstandswert,
            gebuerensatz=verfahrensgebuehr_satz,
            einfache_gebuehr=einfache,
            gebuehr=verfahrensgebuehr,
            rechtsgrundlage="Nr. 3100 VV RVG"
        ))

        # Terminsgebühr
        if mit_termin:
            _, terminsgebuehr = self.berechne_gebuehr(gegenstandswert, terminsgebuehr_satz)
            positionen.append(Gebuehrenposition(
                bezeichnung="Terminsgebühr",
                gebuehrenart=Gebuehrenart.TERMINSGEBUEHR,
                gegenstandswert=gegenstandswert,
                gebuerensatz=terminsgebuehr_satz,
                einfache_gebuehr=einfache,
                gebuehr=terminsgebuehr,
                rechtsgrundlage="Nr. 3104 VV RVG"
            ))

        # Einigungsgebühr
        if mit_einigung:
            _, einigungsgebuehr = self.berechne_gebuehr(gegenstandswert, 1.0)
            positionen.append(Gebuehrenposition(
                bezeichnung="Einigungsgebühr (gerichtlich)",
                gebuehrenart=Gebuehrenart.EINIGUNGSGEBUEHR_GERICHT,
                gegenstandswert=gegenstandswert,
                gebuerensatz=1.0,
                einfache_gebuehr=einfache,
                gebuehr=einigungsgebuehr,
                rechtsgrundlage="Nr. 1003 VV RVG"
            ))

        summe = sum(p.gebuehr for p in positionen)
        auslagen = self.berechne_auslagenpauschale(summe)
        netto = summe + auslagen
        mwst = round(netto * self.mwst_satz, 2)
        gesamt = netto + mwst

        return RVGErgebnis(
            gegenstandswert=gegenstandswert,
            positionen=positionen,
            summe_gebuehren=summe,
            auslagenpauschale=auslagen,
            mehrwertsteuer=mwst,
            gesamtbetrag=gesamt,
            hinweise=hinweise
        )

    def berechne_scheidungsverfahren(
        self,
        nettoeinkommen_a: float,
        nettoeinkommen_b: float,
        anzahl_versorgungsanrechte: int = 2,
        mit_zugewinn: bool = False,
        zugewinn_betrag: float = 0.0,
        mit_unterhalt: bool = False,
        unterhalt_monatlich: float = 0.0
    ) -> RVGErgebnis:
        """
        Berechnet die Gebühren für ein Scheidungsverfahren mit Folgesachen

        Berücksichtigt:
        - Ehescheidung (§ 43 FamGKG)
        - Versorgungsausgleich (§ 50 FamGKG)
        - Optional: Zugewinnausgleich
        - Optional: Unterhalt
        """
        positionen = []
        hinweise = []
        gesamt_gw = 0.0

        # 1. Ehescheidung
        gw_scheidung = self.berechne_gegenstandswert_ehescheidung(
            nettoeinkommen_a, nettoeinkommen_b
        )
        hinweise.append(f"Gegenstandswert Ehescheidung: {gw_scheidung:,.2f}€ (§ 43 FamGKG)")
        gesamt_gw += gw_scheidung

        # 2. Versorgungsausgleich
        if anzahl_versorgungsanrechte > 0:
            gw_va = self.berechne_gegenstandswert_versorgungsausgleich(
                gw_scheidung, anzahl_versorgungsanrechte
            )
            hinweise.append(
                f"Gegenstandswert Versorgungsausgleich: {gw_va:,.2f}€ "
                f"({anzahl_versorgungsanrechte} Anrechte, § 50 FamGKG)"
            )
            gesamt_gw += gw_va

        # 3. Zugewinnausgleich
        if mit_zugewinn and zugewinn_betrag > 0:
            hinweise.append(
                f"Gegenstandswert Zugewinnausgleich: {zugewinn_betrag:,.2f}€"
            )
            gesamt_gw += zugewinn_betrag

        # 4. Unterhalt
        if mit_unterhalt and unterhalt_monatlich > 0:
            gw_unterhalt = self.berechne_gegenstandswert_unterhalt(unterhalt_monatlich)
            hinweise.append(
                f"Gegenstandswert Unterhalt: {gw_unterhalt:,.2f}€ "
                f"(12 × {unterhalt_monatlich:,.2f}€, § 51 FamGKG)"
            )
            gesamt_gw += gw_unterhalt

        hinweise.append(f"Gesamtgegenstandswert: {gesamt_gw:,.2f}€")

        # Gebühren berechnen (gerichtlich mit Termin)
        einfache = self.ermittle_einfache_gebuehr(gesamt_gw)

        # Verfahrensgebühr 1,3
        _, verfahrensgebuehr = self.berechne_gebuehr(gesamt_gw, 1.3)
        positionen.append(Gebuehrenposition(
            bezeichnung="Verfahrensgebühr",
            gebuehrenart=Gebuehrenart.VERFAHRENSGEBUEHR,
            gegenstandswert=gesamt_gw,
            gebuerensatz=1.3,
            einfache_gebuehr=einfache,
            gebuehr=verfahrensgebuehr,
            rechtsgrundlage="Nr. 3100 VV RVG"
        ))

        # Terminsgebühr 1,2
        _, terminsgebuehr = self.berechne_gebuehr(gesamt_gw, 1.2)
        positionen.append(Gebuehrenposition(
            bezeichnung="Terminsgebühr",
            gebuehrenart=Gebuehrenart.TERMINSGEBUEHR,
            gegenstandswert=gesamt_gw,
            gebuerensatz=1.2,
            einfache_gebuehr=einfache,
            gebuehr=terminsgebuehr,
            rechtsgrundlage="Nr. 3104 VV RVG"
        ))

        summe = sum(p.gebuehr for p in positionen)
        auslagen = self.berechne_auslagenpauschale(summe)
        netto = summe + auslagen
        mwst = round(netto * self.mwst_satz, 2)
        gesamt = netto + mwst

        return RVGErgebnis(
            gegenstandswert=gesamt_gw,
            positionen=positionen,
            summe_gebuehren=summe,
            auslagenpauschale=auslagen,
            mehrwertsteuer=mwst,
            gesamtbetrag=gesamt,
            hinweise=hinweise,
            berechnungsdetails={
                "gw_scheidung": gw_scheidung,
                "gw_versorgungsausgleich": gw_scheidung * 0.10 * anzahl_versorgungsanrechte
                if anzahl_versorgungsanrechte > 0 else 0,
                "gw_zugewinn": zugewinn_betrag if mit_zugewinn else 0,
                "gw_unterhalt": unterhalt_monatlich * 12 if mit_unterhalt else 0,
            }
        )

    def berechne_erstberatung(self, ist_verbraucher: bool = True) -> RVGErgebnis:
        """
        Berechnet die Erstberatungsgebühr

        Verbraucher: max. 190€ (§ 34 Abs. 1 S. 3 RVG)
        Unternehmer: Nach Vereinbarung
        """
        if ist_verbraucher:
            gebuehr = self.pauschalen["erstberatung_verbraucher"]
            hinweis = "Erstberatung Verbraucher (§ 34 Abs. 1 S. 3 RVG)"
        else:
            gebuehr = self.pauschalen["weitere_beratung"]
            hinweis = "Beratung nach Vereinbarung"

        mwst = round(gebuehr * self.mwst_satz, 2)

        return RVGErgebnis(
            gegenstandswert=0,
            positionen=[Gebuehrenposition(
                bezeichnung="Erstberatung",
                gebuehrenart=Gebuehrenart.BERATUNGSGEBUEHR,
                gegenstandswert=0,
                gebuerensatz=0,
                einfache_gebuehr=0,
                gebuehr=gebuehr,
                rechtsgrundlage="§ 34 RVG"
            )],
            summe_gebuehren=gebuehr,
            auslagenpauschale=0,
            mehrwertsteuer=mwst,
            gesamtbetrag=gebuehr + mwst,
            hinweise=[hinweis]
        )

    def formatiere_ergebnis(self, ergebnis: RVGErgebnis) -> str:
        """Formatiert das Ergebnis als lesbaren Text"""
        lines = [
            "=" * 65,
            "RVG-GEBÜHRENBERECHNUNG",
            "=" * 65,
            "",
        ]

        if ergebnis.gegenstandswert > 0:
            lines.append(f"Gegenstandswert: {ergebnis.gegenstandswert:>15,.2f} €")
            lines.append("")

        lines.extend([
            "-" * 65,
            "GEBÜHRENPOSITIONEN:",
            "-" * 65,
        ])

        for pos in ergebnis.positionen:
            if pos.gebuerensatz > 0:
                lines.append(
                    f"{pos.bezeichnung:30} {pos.gebuerensatz:.1f} × {pos.einfache_gebuehr:>8,.2f}€ "
                    f"= {pos.gebuehr:>10,.2f} €"
                )
            else:
                lines.append(f"{pos.bezeichnung:30} {pos.gebuehr:>30,.2f} €")
            if pos.rechtsgrundlage:
                lines.append(f"  ({pos.rechtsgrundlage})")

        lines.extend([
            "",
            "-" * 65,
            f"{'Zwischensumme Gebühren:':45} {ergebnis.summe_gebuehren:>12,.2f} €",
        ])

        if ergebnis.auslagenpauschale > 0:
            lines.append(
                f"{'Auslagenpauschale (Nr. 7002 VV RVG):':45} {ergebnis.auslagenpauschale:>12,.2f} €"
            )

        lines.extend([
            f"{'Nettobetrag:':45} {ergebnis.summe_gebuehren + ergebnis.auslagenpauschale:>12,.2f} €",
            f"{'MwSt. 19%:':45} {ergebnis.mehrwertsteuer:>12,.2f} €",
            "-" * 65,
            f"{'GESAMTBETRAG:':45} {ergebnis.gesamtbetrag:>12,.2f} €",
            "-" * 65,
        ])

        if ergebnis.hinweise:
            lines.extend([
                "",
                "HINWEISE:",
            ])
            for hinweis in ergebnis.hinweise:
                lines.append(f"  • {hinweis}")

        lines.append("=" * 65)

        return "\n".join(lines)
