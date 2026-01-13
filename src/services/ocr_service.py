"""
OCR-Service fuer Texterkennung aus gescannten Dokumenten

Verwendet pytesseract fuer OCR und pdf2image fuer PDF-Konvertierung.
Unterstuetzt sowohl Demo-Modus als auch echte OCR-Verarbeitung.
"""

import os
import io
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Optionale Imports - werden nur benoetigt wenn echte OCR verwendet wird
try:
    import pytesseract
    from PIL import Image
    TESSERACT_VERFUEGBAR = True
except ImportError:
    TESSERACT_VERFUEGBAR = False

try:
    from pdf2image import convert_from_bytes, convert_from_path
    PDF2IMAGE_VERFUEGBAR = True
except ImportError:
    PDF2IMAGE_VERFUEGBAR = False


class OCRSprache(Enum):
    """Unterstuetzte OCR-Sprachen"""
    DEUTSCH = "deu"
    ENGLISCH = "eng"
    DEUTSCH_ENGLISCH = "deu+eng"


class DokumentTyp(Enum):
    """Erkannte Dokumenttypen"""
    GEHALTSABRECHNUNG = "gehaltsabrechnung"
    STEUERBESCHEID = "steuerbescheid"
    KONTOAUSZUG = "kontoauszug"
    VERTRAG = "vertrag"
    BESCHEID = "bescheid"
    SCHRIFTSATZ = "schriftsatz"
    RECHNUNG = "rechnung"
    UNBEKANNT = "unbekannt"


@dataclass
class OCRErgebnis:
    """Ergebnis einer OCR-Verarbeitung"""
    erfolg: bool
    text: str
    konfidenz: float  # 0.0 - 1.0
    sprache: str
    seiten_anzahl: int
    verarbeitungszeit_ms: int
    erkannter_dokumenttyp: Optional[DokumentTyp] = None
    extrahierte_daten: Dict = field(default_factory=dict)
    fehler: Optional[str] = None


@dataclass
class SeitenOCR:
    """OCR-Ergebnis einer einzelnen Seite"""
    seite: int
    text: str
    konfidenz: float
    bounding_boxes: List[Dict] = field(default_factory=list)


class OCRService:
    """
    OCR-Service fuer Texterkennung

    Unterstuetzt:
    - Bilder (PNG, JPG, TIFF, BMP)
    - PDF-Dokumente (werden in Bilder konvertiert)
    - Mehrsprachige Erkennung (Deutsch/Englisch)
    - Automatische Dokumenttyp-Erkennung
    - Extraktion strukturierter Daten (Betraege, Daten, Namen)
    """

    def __init__(self, demo_modus: bool = True, tesseract_pfad: str = None):
        """
        Initialisiert den OCR-Service

        Args:
            demo_modus: Wenn True, werden Demo-Daten zurueckgegeben
            tesseract_pfad: Optionaler Pfad zur Tesseract-Installation
        """
        self.demo_modus = demo_modus

        if tesseract_pfad and TESSERACT_VERFUEGBAR:
            pytesseract.pytesseract.tesseract_cmd = tesseract_pfad

        # Schluesselwoerter fuer Dokumenttyp-Erkennung
        self.dokumenttyp_keywords = {
            DokumentTyp.GEHALTSABRECHNUNG: [
                "gehaltsabrechnung", "lohnabrechnung", "bruttolohn",
                "nettolohn", "sozialversicherung", "lohnsteuer",
                "arbeitgeber", "arbeitnehmer", "vergütung"
            ],
            DokumentTyp.STEUERBESCHEID: [
                "steuerbescheid", "finanzamt", "einkommensteuer",
                "steuernummer", "festsetzung", "veranlagung"
            ],
            DokumentTyp.KONTOAUSZUG: [
                "kontoauszug", "haben", "soll", "kontonummer",
                "bankleitzahl", "iban", "kontostand", "umsatz"
            ],
            DokumentTyp.VERTRAG: [
                "vertrag", "vereinbarung", "vertragspartner",
                "kuendigung", "laufzeit", "unterschrift"
            ],
            DokumentTyp.BESCHEID: [
                "bescheid", "amt", "behoerde", "antrag",
                "bewilligung", "ablehnung", "widerspruch"
            ],
            DokumentTyp.SCHRIFTSATZ: [
                "klaeger", "beklagter", "gericht", "aktenzeichen",
                "antrag", "klage", "berufung", "rechtsanwalt"
            ],
            DokumentTyp.RECHNUNG: [
                "rechnung", "rechnungsnummer", "betrag", "mwst",
                "zahlungsziel", "bankverbindung", "steuernummer"
            ]
        }

    def ist_verfuegbar(self) -> Tuple[bool, str]:
        """
        Prueft ob OCR verfuegbar ist

        Returns:
            Tuple aus (verfuegbar, meldung)
        """
        if self.demo_modus:
            return True, "OCR-Service laeuft im Demo-Modus"

        if not TESSERACT_VERFUEGBAR:
            return False, "pytesseract nicht installiert. Bitte 'pip install pytesseract pillow' ausfuehren."

        if not PDF2IMAGE_VERFUEGBAR:
            return False, "pdf2image nicht installiert. Bitte 'pip install pdf2image' ausfuehren."

        # Teste ob Tesseract erreichbar ist
        try:
            pytesseract.get_tesseract_version()
            return True, "OCR-Service ist bereit"
        except Exception as e:
            return False, f"Tesseract nicht gefunden oder nicht konfiguriert: {str(e)}"

    def verarbeite_bild(
        self,
        bild_bytes: bytes,
        sprache: OCRSprache = OCRSprache.DEUTSCH_ENGLISCH
    ) -> OCRErgebnis:
        """
        Fuehrt OCR auf einem Bild durch

        Args:
            bild_bytes: Bilddaten als Bytes
            sprache: Sprache fuer OCR

        Returns:
            OCRErgebnis mit erkanntem Text
        """
        start_zeit = datetime.now()

        if self.demo_modus:
            return self._demo_ocr_ergebnis(seiten=1)

        if not TESSERACT_VERFUEGBAR:
            return OCRErgebnis(
                erfolg=False,
                text="",
                konfidenz=0.0,
                sprache=sprache.value,
                seiten_anzahl=0,
                verarbeitungszeit_ms=0,
                fehler="OCR nicht verfuegbar (pytesseract nicht installiert)"
            )

        try:
            # Bild laden
            image = Image.open(io.BytesIO(bild_bytes))

            # OCR durchfuehren
            ocr_data = pytesseract.image_to_data(
                image,
                lang=sprache.value,
                output_type=pytesseract.Output.DICT
            )

            # Text extrahieren
            text = pytesseract.image_to_string(image, lang=sprache.value)

            # Konfidenz berechnen
            konfidenzen = [int(c) for c in ocr_data['conf'] if int(c) > 0]
            durchschn_konfidenz = sum(konfidenzen) / len(konfidenzen) / 100 if konfidenzen else 0.0

            verarbeitungszeit = int((datetime.now() - start_zeit).total_seconds() * 1000)

            # Dokumenttyp erkennen
            dokumenttyp = self._erkenne_dokumenttyp(text)

            # Daten extrahieren
            extrahierte_daten = self._extrahiere_daten(text, dokumenttyp)

            return OCRErgebnis(
                erfolg=True,
                text=text,
                konfidenz=durchschn_konfidenz,
                sprache=sprache.value,
                seiten_anzahl=1,
                verarbeitungszeit_ms=verarbeitungszeit,
                erkannter_dokumenttyp=dokumenttyp,
                extrahierte_daten=extrahierte_daten
            )

        except Exception as e:
            verarbeitungszeit = int((datetime.now() - start_zeit).total_seconds() * 1000)
            return OCRErgebnis(
                erfolg=False,
                text="",
                konfidenz=0.0,
                sprache=sprache.value,
                seiten_anzahl=0,
                verarbeitungszeit_ms=verarbeitungszeit,
                fehler=str(e)
            )

    def verarbeite_pdf(
        self,
        pdf_bytes: bytes,
        sprache: OCRSprache = OCRSprache.DEUTSCH_ENGLISCH,
        max_seiten: int = None,
        dpi: int = 200
    ) -> OCRErgebnis:
        """
        Fuehrt OCR auf einem PDF durch

        Args:
            pdf_bytes: PDF-Daten als Bytes
            sprache: Sprache fuer OCR
            max_seiten: Maximale Anzahl zu verarbeitender Seiten
            dpi: Aufloesung fuer PDF zu Bild Konvertierung

        Returns:
            OCRErgebnis mit erkanntem Text aller Seiten
        """
        start_zeit = datetime.now()

        if self.demo_modus:
            return self._demo_ocr_ergebnis(seiten=5)

        if not PDF2IMAGE_VERFUEGBAR:
            return OCRErgebnis(
                erfolg=False,
                text="",
                konfidenz=0.0,
                sprache=sprache.value,
                seiten_anzahl=0,
                verarbeitungszeit_ms=0,
                fehler="PDF-Konvertierung nicht verfuegbar (pdf2image nicht installiert)"
            )

        if not TESSERACT_VERFUEGBAR:
            return OCRErgebnis(
                erfolg=False,
                text="",
                konfidenz=0.0,
                sprache=sprache.value,
                seiten_anzahl=0,
                verarbeitungszeit_ms=0,
                fehler="OCR nicht verfuegbar (pytesseract nicht installiert)"
            )

        try:
            # PDF in Bilder konvertieren
            bilder = convert_from_bytes(pdf_bytes, dpi=dpi)

            if max_seiten:
                bilder = bilder[:max_seiten]

            alle_texte = []
            alle_konfidenzen = []
            seiten_ergebnisse = []

            for seite_nr, bild in enumerate(bilder, 1):
                # OCR fuer jede Seite
                ocr_data = pytesseract.image_to_data(
                    bild,
                    lang=sprache.value,
                    output_type=pytesseract.Output.DICT
                )

                seiten_text = pytesseract.image_to_string(bild, lang=sprache.value)
                alle_texte.append(f"--- Seite {seite_nr} ---\n{seiten_text}")

                # Konfidenz berechnen
                konfidenzen = [int(c) for c in ocr_data['conf'] if int(c) > 0]
                if konfidenzen:
                    seiten_konfidenz = sum(konfidenzen) / len(konfidenzen) / 100
                    alle_konfidenzen.append(seiten_konfidenz)

                seiten_ergebnisse.append(SeitenOCR(
                    seite=seite_nr,
                    text=seiten_text,
                    konfidenz=seiten_konfidenz if konfidenzen else 0.0
                ))

            gesamt_text = "\n\n".join(alle_texte)
            durchschn_konfidenz = sum(alle_konfidenzen) / len(alle_konfidenzen) if alle_konfidenzen else 0.0

            verarbeitungszeit = int((datetime.now() - start_zeit).total_seconds() * 1000)

            # Dokumenttyp erkennen
            dokumenttyp = self._erkenne_dokumenttyp(gesamt_text)

            # Daten extrahieren
            extrahierte_daten = self._extrahiere_daten(gesamt_text, dokumenttyp)
            extrahierte_daten['seiten_details'] = [
                {'seite': s.seite, 'konfidenz': s.konfidenz}
                for s in seiten_ergebnisse
            ]

            return OCRErgebnis(
                erfolg=True,
                text=gesamt_text,
                konfidenz=durchschn_konfidenz,
                sprache=sprache.value,
                seiten_anzahl=len(bilder),
                verarbeitungszeit_ms=verarbeitungszeit,
                erkannter_dokumenttyp=dokumenttyp,
                extrahierte_daten=extrahierte_daten
            )

        except Exception as e:
            verarbeitungszeit = int((datetime.now() - start_zeit).total_seconds() * 1000)
            return OCRErgebnis(
                erfolg=False,
                text="",
                konfidenz=0.0,
                sprache=sprache.value,
                seiten_anzahl=0,
                verarbeitungszeit_ms=verarbeitungszeit,
                fehler=str(e)
            )

    def _erkenne_dokumenttyp(self, text: str) -> DokumentTyp:
        """Erkennt den Dokumenttyp anhand von Schluesselwoertern"""
        text_lower = text.lower()

        beste_uebereinstimmung = DokumentTyp.UNBEKANNT
        hoechste_treffer = 0

        for dokumenttyp, keywords in self.dokumenttyp_keywords.items():
            treffer = sum(1 for kw in keywords if kw in text_lower)
            if treffer > hoechste_treffer:
                hoechste_treffer = treffer
                beste_uebereinstimmung = dokumenttyp

        # Mindestens 2 Treffer fuer eine Klassifizierung
        if hoechste_treffer >= 2:
            return beste_uebereinstimmung
        return DokumentTyp.UNBEKANNT

    def _extrahiere_daten(self, text: str, dokumenttyp: DokumentTyp) -> Dict:
        """Extrahiert strukturierte Daten aus dem Text"""
        import re

        daten = {}

        # Geldbetraege extrahieren
        betraege = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*(?:EUR|€|Euro)?)', text)
        if betraege:
            daten['erkannte_betraege'] = betraege[:10]  # Max 10

        # Daten extrahieren (DD.MM.YYYY Format)
        datum_matches = re.findall(r'\b(\d{1,2}\.\d{1,2}\.\d{4})\b', text)
        if datum_matches:
            daten['erkannte_daten'] = list(set(datum_matches))[:5]  # Max 5, unique

        # IBAN extrahieren
        iban = re.findall(r'[A-Z]{2}\d{2}\s*(?:\d{4}\s*){4,5}\d{0,4}', text.replace(' ', ''))
        if iban:
            daten['iban'] = iban[0]

        # Aktenzeichen extrahieren
        az = re.findall(r'(?:Az\.?|Aktenzeichen):?\s*(\d+\s*[A-Za-z]*\s*\d+(?:/\d+)?)', text)
        if az:
            daten['aktenzeichen'] = az[0]

        # Dokumenttyp-spezifische Extraktion
        if dokumenttyp == DokumentTyp.GEHALTSABRECHNUNG:
            # Brutto/Netto suchen
            brutto = re.search(r'Brutto[^\d]*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', text)
            if brutto:
                daten['bruttolohn'] = brutto.group(1)

            netto = re.search(r'Netto[^\d]*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', text)
            if netto:
                daten['nettolohn'] = netto.group(1)

        elif dokumenttyp == DokumentTyp.STEUERBESCHEID:
            # Zu versteuerndes Einkommen
            zve = re.search(r'zu versteuerndes Einkommen[^\d]*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', text, re.IGNORECASE)
            if zve:
                daten['zu_versteuerndes_einkommen'] = zve.group(1)

        return daten

    def _demo_ocr_ergebnis(self, seiten: int = 1) -> OCRErgebnis:
        """Generiert ein Demo-OCR-Ergebnis"""

        demo_texte = {
            1: """
GEHALTSABRECHNUNG

Arbeitgeber: Muster GmbH
Mitarbeiter: Max Mustermann
Personalnummer: 12345
Abrechnungsmonat: Dezember 2025

Bruttolohn:                    4.500,00 EUR
Lohnsteuer:                      750,00 EUR
Solidaritätszuschlag:            41,25 EUR
Kirchensteuer:                   67,50 EUR
Krankenversicherung:            369,00 EUR
Rentenversicherung:             418,50 EUR
Arbeitslosenversicherung:        58,50 EUR
Pflegeversicherung:              76,50 EUR

Nettolohn:                     2.718,75 EUR

IBAN: DE89 3704 0044 0532 0130 00
""",
            5: """
--- Seite 1 ---
GEHALTSABRECHNUNG

Arbeitgeber: Schmidt & Partner GbR
Mitarbeiter: Anna Schmidt
Personalnummer: 54321
Abrechnungsmonat: Dezember 2025

Bruttolohn:                    5.200,00 EUR

--- Seite 2 ---
SOZIALVERSICHERUNGSBEITRAEGE

Krankenversicherung AN:          425,36 EUR
Rentenversicherung AN:           483,60 EUR
Arbeitslosenversicherung AN:      67,60 EUR
Pflegeversicherung AN:            88,40 EUR

Gesamt AN-Beitraege:           1.064,96 EUR

--- Seite 3 ---
STEUERABZUEGE

Lohnsteuer:                      980,00 EUR
Solidaritätszuschlag:             53,90 EUR
Kirchensteuer:                    88,20 EUR

Gesamt Steuerabzuege:          1.122,10 EUR

--- Seite 4 ---
WEITERE BEZUEGE

Firmenwagen (geldwerter Vorteil): 350,00 EUR
Essenszuschuss:                    75,00 EUR
Fahrtkostenzuschuss:              100,00 EUR

--- Seite 5 ---
ZUSAMMENFASSUNG

Gesamtbrutto:                  5.725,00 EUR
Abzuege gesamt:                2.187,06 EUR
Nettolohn:                     3.537,94 EUR

Auszahlung erfolgt auf:
IBAN: DE44 5001 0517 5407 3249 31
BIC: INGDDEFFXXX

Erstellungsdatum: 23.12.2025
"""
        }

        text = demo_texte.get(seiten, demo_texte[1])

        return OCRErgebnis(
            erfolg=True,
            text=text,
            konfidenz=0.92,
            sprache="deu+eng",
            seiten_anzahl=seiten,
            verarbeitungszeit_ms=seiten * 450,
            erkannter_dokumenttyp=DokumentTyp.GEHALTSABRECHNUNG,
            extrahierte_daten={
                'erkannte_betraege': ['4.500,00 EUR', '2.718,75 EUR'] if seiten == 1 else ['5.200,00 EUR', '3.537,94 EUR'],
                'erkannte_daten': ['23.12.2025'] if seiten > 1 else [],
                'iban': 'DE89370400440532013000' if seiten == 1 else 'DE44500105175407324931',
                'bruttolohn': '4.500,00' if seiten == 1 else '5.200,00',
                'nettolohn': '2.718,75' if seiten == 1 else '3.537,94'
            }
        )


def ocr_bild(bild_bytes: bytes, demo_modus: bool = True) -> OCRErgebnis:
    """
    Komfort-Funktion fuer OCR auf einem Bild

    Args:
        bild_bytes: Bilddaten
        demo_modus: Demo-Modus aktivieren

    Returns:
        OCRErgebnis
    """
    service = OCRService(demo_modus=demo_modus)
    return service.verarbeite_bild(bild_bytes)


def ocr_pdf(pdf_bytes: bytes, demo_modus: bool = True) -> OCRErgebnis:
    """
    Komfort-Funktion fuer OCR auf einem PDF

    Args:
        pdf_bytes: PDF-Daten
        demo_modus: Demo-Modus aktivieren

    Returns:
        OCRErgebnis
    """
    service = OCRService(demo_modus=demo_modus)
    return service.verarbeite_pdf(pdf_bytes)
