"""
Import-Service fuer FamilyKom

Bietet echte Import-Funktionalitaet fuer:
- PDF-Dateien mit Lesezeichen-Extraktion
- ZIP-Archive mit Struktur-Erkennung
- Aktenzeichen-Erkennung aus Dateinamen und Inhalten
"""

import io
import os
import re
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime

# PDF-Bibliotheken
try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


@dataclass
class Lesezeichen:
    """Repraesentiert ein PDF-Lesezeichen (Bookmark)"""
    titel: str
    seite: int
    ebene: int
    kinder: List['Lesezeichen'] = field(default_factory=list)


@dataclass
class ExtrahiertesDokument:
    """Repraesentiert ein aus einem PDF extrahiertes Teildokument"""
    name: str
    start_seite: int
    end_seite: int
    seitenanzahl: int
    pdf_bytes: Optional[bytes] = None
    text_vorschau: str = ""


@dataclass
class ErkannteAkte:
    """Repraesentiert eine aus dem Import erkannte Akte"""
    aktenzeichen: str
    mandant: str = ""
    gegner: str = ""
    typ: str = ""
    angelegt: str = ""
    dokumente: List[str] = field(default_factory=list)
    dokument_count: int = 0
    quelle: str = ""


@dataclass
class ImportErgebnis:
    """Gesamtergebnis eines Imports"""
    quelle: str
    erfolgreich: bool
    akten: List[ErkannteAkte] = field(default_factory=list)
    dokumente: List[ExtrahiertesDokument] = field(default_factory=list)
    dokumente_ohne_akte: List[Dict] = field(default_factory=list)
    lesezeichen: List[Lesezeichen] = field(default_factory=list)
    fehler: List[str] = field(default_factory=list)
    hinweise: List[str] = field(default_factory=list)


# Regex-Muster fuer Aktenzeichen-Erkennung
AKTENZEICHEN_MUSTER = [
    r'\b(\d{4}[/-]\d{3,5})\b',  # 2026/0001 oder 2026-0001
    r'\bAz\.?\s*:?\s*(\d{4}[/-]\d{3,5})\b',  # Az.: 2026/0001
    r'\bAktenzeichen\s*:?\s*(\d{4}[/-]\d{3,5})\b',  # Aktenzeichen: 2026/0001
    r'\b(\d+\s*[A-Z]+\s*\d+[/-]\d+)\b',  # 12 F 123/26 (Gerichtsaktenzeichen)
]

# Muster fuer Parteinamen
PARTEI_MUSTER = [
    r'([A-ZÄÖÜ][a-zäöüß]+),\s*([A-ZÄÖÜ][a-zäöüß]+)\s*\.?/?\.?\s*([A-ZÄÖÜ][a-zäöüß]+),\s*([A-ZÄÖÜ][a-zäöüß]+)',  # Schmidt, Maria ./. Schmidt, Thomas
    r'Antragsteller(?:in)?:\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)',
    r'Antragsgegner(?:in)?:\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)',
]


def extrahiere_lesezeichen_aus_pdf(pdf_file: BinaryIO) -> List[Lesezeichen]:
    """
    Extrahiert alle Lesezeichen (Bookmarks) aus einem PDF.

    Args:
        pdf_file: PDF-Datei als Binary-Stream

    Returns:
        Liste von Lesezeichen-Objekten
    """
    if not PYPDF_AVAILABLE:
        return []

    lesezeichen_liste = []

    try:
        reader = PdfReader(pdf_file)

        def verarbeite_outline(outline, ebene=1) -> List[Lesezeichen]:
            """Rekursive Verarbeitung der Outline-Struktur"""
            ergebnis = []

            if outline is None:
                return ergebnis

            for item in outline:
                if isinstance(item, list):
                    # Verschachtelte Liste = Unterebene
                    if ergebnis:
                        ergebnis[-1].kinder = verarbeite_outline(item, ebene + 1)
                else:
                    # Einzelnes Lesezeichen
                    try:
                        titel = item.title if hasattr(item, 'title') else str(item)

                        # Seitennummer ermitteln
                        seite = 0
                        if hasattr(item, 'page'):
                            if item.page is not None:
                                try:
                                    seite = reader.get_page_number(item.page) + 1
                                except:
                                    seite = 1

                        lz = Lesezeichen(
                            titel=titel,
                            seite=seite,
                            ebene=ebene
                        )
                        ergebnis.append(lz)
                    except Exception as e:
                        continue

            return ergebnis

        if reader.outline:
            lesezeichen_liste = verarbeite_outline(reader.outline)

    except Exception as e:
        print(f"Fehler beim Lesen der Lesezeichen: {e}")

    return lesezeichen_liste


def extrahiere_text_aus_pdf(pdf_file: BinaryIO, max_seiten: int = 5) -> str:
    """
    Extrahiert Text aus den ersten Seiten eines PDFs.

    Args:
        pdf_file: PDF-Datei als Binary-Stream
        max_seiten: Maximale Anzahl zu lesender Seiten

    Returns:
        Extrahierter Text
    """
    text = ""

    if PDFPLUMBER_AVAILABLE:
        try:
            pdf_file.seek(0)
            with pdfplumber.open(pdf_file) as pdf:
                for i, page in enumerate(pdf.pages[:max_seiten]):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber Fehler: {e}")

    if not text and PYPDF_AVAILABLE:
        try:
            pdf_file.seek(0)
            reader = PdfReader(pdf_file)
            for i, page in enumerate(reader.pages[:max_seiten]):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except:
                    continue
        except Exception as e:
            print(f"pypdf Fehler: {e}")

    return text


def erkenne_aktenzeichen(text: str, dateiname: str = "") -> Optional[str]:
    """
    Versucht ein Aktenzeichen aus Text oder Dateinamen zu erkennen.

    Args:
        text: Text zum Durchsuchen
        dateiname: Dateiname zum Durchsuchen

    Returns:
        Erkanntes Aktenzeichen oder None
    """
    # Zuerst im Dateinamen suchen
    for muster in AKTENZEICHEN_MUSTER:
        match = re.search(muster, dateiname)
        if match:
            return match.group(1)

    # Dann im Text suchen
    for muster in AKTENZEICHEN_MUSTER:
        match = re.search(muster, text)
        if match:
            return match.group(1)

    return None


def erkenne_parteien(text: str) -> Tuple[str, str]:
    """
    Versucht Mandant und Gegner aus dem Text zu erkennen.

    Args:
        text: Text zum Durchsuchen

    Returns:
        Tuple (mandant, gegner)
    """
    mandant = ""
    gegner = ""

    # Versuche ./. Muster
    match = re.search(
        r'([A-ZÄÖÜ][a-zäöüß]+),\s*([A-ZÄÖÜ][a-zäöüß]+)\s*\.?/?\.?\s*([A-ZÄÖÜ][a-zäöüß]+),\s*([A-ZÄÖÜ][a-zäöüß]+)',
        text
    )
    if match:
        mandant = f"{match.group(1)}, {match.group(2)}"
        gegner = f"{match.group(3)}, {match.group(4)}"
        return mandant, gegner

    # Versuche Antragsteller/Antragsgegner
    match_as = re.search(r'Antragsteller(?:in)?:\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)', text)
    match_ag = re.search(r'Antragsgegner(?:in)?:\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)', text)

    if match_as:
        mandant = match_as.group(1)
    if match_ag:
        gegner = match_ag.group(1)

    return mandant, gegner


def erkenne_verfahrensart(text: str, dateiname: str = "") -> str:
    """
    Versucht die Verfahrensart zu erkennen.

    Args:
        text: Text zum Durchsuchen
        dateiname: Dateiname zum Durchsuchen

    Returns:
        Erkannte Verfahrensart
    """
    kombinierter_text = (text + " " + dateiname).lower()

    if "scheidung" in kombinierter_text:
        return "Scheidung"
    elif "kindesunterhalt" in kombinierter_text or "minderjährig" in kombinierter_text:
        return "Kindesunterhalt"
    elif "trennungsunterhalt" in kombinierter_text:
        return "Trennungsunterhalt"
    elif "nachehelich" in kombinierter_text:
        return "Nachehelicher Unterhalt"
    elif "zugewinn" in kombinierter_text:
        return "Zugewinnausgleich"
    elif "versorgungsausgleich" in kombinierter_text:
        return "Versorgungsausgleich"
    elif "sorgerecht" in kombinierter_text:
        return "Sorgerecht"
    elif "umgang" in kombinierter_text:
        return "Umgangsrecht"

    return "Familienrecht"


def teile_pdf_nach_lesezeichen(
    pdf_file: BinaryIO,
    lesezeichen: List[Lesezeichen],
    nur_hauptebene: bool = True
) -> List[ExtrahiertesDokument]:
    """
    Teilt ein PDF anhand der Lesezeichen in einzelne Dokumente.

    Args:
        pdf_file: PDF-Datei als Binary-Stream
        lesezeichen: Liste der Lesezeichen
        nur_hauptebene: Nur Hauptlesezeichen (Ebene 1) verwenden

    Returns:
        Liste der extrahierten Dokumente
    """
    if not PYPDF_AVAILABLE or not lesezeichen:
        return []

    dokumente = []

    try:
        pdf_file.seek(0)
        reader = PdfReader(pdf_file)
        total_pages = len(reader.pages)

        # Lesezeichen filtern
        if nur_hauptebene:
            relevante_lz = [lz for lz in lesezeichen if lz.ebene == 1]
        else:
            # Alle Lesezeichen flach machen
            def flatten(lz_liste):
                result = []
                for lz in lz_liste:
                    result.append(lz)
                    if lz.kinder:
                        result.extend(flatten(lz.kinder))
                return result
            relevante_lz = flatten(lesezeichen)

        # Nach Seite sortieren
        relevante_lz = sorted(relevante_lz, key=lambda x: x.seite)

        for i, lz in enumerate(relevante_lz):
            start_seite = lz.seite - 1  # 0-basiert

            # Ende ist entweder naechstes Lesezeichen oder Ende des Dokuments
            if i + 1 < len(relevante_lz):
                end_seite = relevante_lz[i + 1].seite - 1
            else:
                end_seite = total_pages

            # PDF-Teil extrahieren
            writer = PdfWriter()
            for page_num in range(start_seite, end_seite):
                if page_num < total_pages:
                    writer.add_page(reader.pages[page_num])

            # In Bytes speichern
            pdf_bytes_io = io.BytesIO()
            writer.write(pdf_bytes_io)
            pdf_bytes = pdf_bytes_io.getvalue()

            # Dateiname aus Lesezeichen-Titel erstellen
            safe_name = re.sub(r'[^\w\s-]', '', lz.titel)
            safe_name = re.sub(r'\s+', '_', safe_name)

            dokument = ExtrahiertesDokument(
                name=f"{safe_name}.pdf",
                start_seite=start_seite + 1,
                end_seite=end_seite,
                seitenanzahl=end_seite - start_seite,
                pdf_bytes=pdf_bytes,
                text_vorschau=lz.titel
            )
            dokumente.append(dokument)

    except Exception as e:
        print(f"Fehler beim Teilen des PDFs: {e}")

    return dokumente


def extrahiere_zip(
    zip_file: BinaryIO,
    ziel_verzeichnis: Optional[str] = None
) -> Tuple[List[str], List[str]]:
    """
    Extrahiert ein ZIP-Archiv.

    Args:
        zip_file: ZIP-Datei als Binary-Stream
        ziel_verzeichnis: Optionales Zielverzeichnis

    Returns:
        Tuple (Liste extrahierter Dateien, Liste von Fehlern)
    """
    extrahierte_dateien = []
    fehler = []

    try:
        zip_file.seek(0)

        with zipfile.ZipFile(zip_file, 'r') as zf:
            # Pruefen ob es ein gueltiges ZIP ist
            if zf.testzip() is not None:
                fehler.append("ZIP-Archiv ist beschaedigt")
                return extrahierte_dateien, fehler

            # Temporaeres Verzeichnis wenn keins angegeben
            if ziel_verzeichnis is None:
                ziel_verzeichnis = tempfile.mkdtemp(prefix="familykom_import_")

            # Alle Dateien extrahieren
            for info in zf.infolist():
                if not info.is_dir():
                    try:
                        zf.extract(info, ziel_verzeichnis)
                        extrahierter_pfad = os.path.join(ziel_verzeichnis, info.filename)
                        extrahierte_dateien.append(extrahierter_pfad)
                    except Exception as e:
                        fehler.append(f"Fehler bei {info.filename}: {str(e)}")

    except zipfile.BadZipFile:
        fehler.append("Keine gueltige ZIP-Datei")
    except Exception as e:
        fehler.append(f"Fehler beim Extrahieren: {str(e)}")

    return extrahierte_dateien, fehler


def analysiere_zip_inhalt(zip_file: BinaryIO) -> Dict:
    """
    Analysiert den Inhalt eines ZIP-Archivs ohne zu extrahieren.

    Args:
        zip_file: ZIP-Datei als Binary-Stream

    Returns:
        Dictionary mit Analyse-Ergebnissen
    """
    ergebnis = {
        "dateien": [],
        "ordner": [],
        "pdf_count": 0,
        "gesamt_groesse": 0,
        "struktur": {}
    }

    try:
        zip_file.seek(0)

        with zipfile.ZipFile(zip_file, 'r') as zf:
            for info in zf.infolist():
                if info.is_dir():
                    ergebnis["ordner"].append(info.filename)
                else:
                    datei_info = {
                        "name": info.filename,
                        "groesse": info.file_size,
                        "komprimiert": info.compress_size,
                        "datum": datetime(*info.date_time).isoformat() if info.date_time else None
                    }
                    ergebnis["dateien"].append(datei_info)
                    ergebnis["gesamt_groesse"] += info.file_size

                    if info.filename.lower().endswith('.pdf'):
                        ergebnis["pdf_count"] += 1

    except Exception as e:
        ergebnis["fehler"] = str(e)

    return ergebnis


def importiere_pdf(pdf_file: BinaryIO, dateiname: str = "") -> ImportErgebnis:
    """
    Hauptfunktion zum Importieren einer PDF-Datei.
    Extrahiert Lesezeichen, erkennt Akten und teilt das Dokument.

    Args:
        pdf_file: PDF-Datei als Binary-Stream
        dateiname: Urspruenglicher Dateiname

    Returns:
        ImportErgebnis mit allen erkannten Daten
    """
    ergebnis = ImportErgebnis(
        quelle="PDF-Import",
        erfolgreich=True
    )

    # 1. Lesezeichen extrahieren
    lesezeichen = extrahiere_lesezeichen_aus_pdf(pdf_file)
    ergebnis.lesezeichen = lesezeichen

    if lesezeichen:
        ergebnis.hinweise.append(f"{len(lesezeichen)} Lesezeichen gefunden")
    else:
        ergebnis.hinweise.append("Keine Lesezeichen im PDF gefunden")

    # 2. Text extrahieren fuer Analyse
    pdf_file.seek(0)
    text = extrahiere_text_aus_pdf(pdf_file)

    # 3. Aktenzeichen erkennen
    aktenzeichen = erkenne_aktenzeichen(text, dateiname)

    # 4. Parteien erkennen
    mandant, gegner = erkenne_parteien(text)

    # 5. Verfahrensart erkennen
    verfahrensart = erkenne_verfahrensart(text, dateiname)

    # 6. Akte erstellen wenn Aktenzeichen gefunden
    if aktenzeichen:
        akte = ErkannteAkte(
            aktenzeichen=aktenzeichen,
            mandant=mandant or "Unbekannt",
            gegner=gegner or "Unbekannt",
            typ=verfahrensart,
            angelegt=datetime.now().strftime("%d.%m.%Y"),
            quelle="PDF-Import"
        )

        # Dokumente aus Lesezeichen
        if lesezeichen:
            pdf_file.seek(0)
            dokumente = teile_pdf_nach_lesezeichen(pdf_file, lesezeichen)
            akte.dokumente = [d.name for d in dokumente]
            akte.dokument_count = len(dokumente)
            ergebnis.dokumente = dokumente
        else:
            akte.dokument_count = 1
            akte.dokumente = [dateiname]

        ergebnis.akten.append(akte)
    else:
        # Kein Aktenzeichen gefunden - als Dokument ohne Akte markieren
        ergebnis.dokumente_ohne_akte.append({
            "name": dateiname,
            "seiten": 0,  # TODO: Seitenanzahl ermitteln
            "text_vorschau": text[:200] if text else ""
        })
        ergebnis.hinweise.append("Kein Aktenzeichen erkannt - manuelle Zuordnung erforderlich")

    return ergebnis


def importiere_zip(zip_file: BinaryIO, dateiname: str = "") -> ImportErgebnis:
    """
    Hauptfunktion zum Importieren eines ZIP-Archivs.
    Extrahiert alle Dateien und analysiert PDFs.

    Args:
        zip_file: ZIP-Datei als Binary-Stream
        dateiname: Urspruenglicher Dateiname

    Returns:
        ImportErgebnis mit allen erkannten Daten
    """
    ergebnis = ImportErgebnis(
        quelle="ZIP-Import",
        erfolgreich=True
    )

    # 1. ZIP-Inhalt analysieren
    analyse = analysiere_zip_inhalt(zip_file)

    ergebnis.hinweise.append(f"{len(analyse['dateien'])} Dateien im Archiv")
    ergebnis.hinweise.append(f"{analyse['pdf_count']} PDF-Dateien gefunden")

    # 2. ZIP extrahieren
    zip_file.seek(0)
    extrahierte_dateien, fehler = extrahiere_zip(zip_file)

    if fehler:
        ergebnis.fehler.extend(fehler)

    # 3. Jede PDF-Datei analysieren
    akten_dict = {}  # Gruppierung nach Aktenzeichen

    for dateipfad in extrahierte_dateien:
        if dateipfad.lower().endswith('.pdf'):
            try:
                with open(dateipfad, 'rb') as pdf_file:
                    pdf_ergebnis = importiere_pdf(pdf_file, os.path.basename(dateipfad))

                    # Akten zusammenfuehren
                    for akte in pdf_ergebnis.akten:
                        if akte.aktenzeichen in akten_dict:
                            # Dokumente zur bestehenden Akte hinzufuegen
                            akten_dict[akte.aktenzeichen].dokumente.extend(akte.dokumente)
                            akten_dict[akte.aktenzeichen].dokument_count += akte.dokument_count
                        else:
                            akten_dict[akte.aktenzeichen] = akte

                    # Dokumente ohne Akte uebernehmen
                    ergebnis.dokumente_ohne_akte.extend(pdf_ergebnis.dokumente_ohne_akte)

            except Exception as e:
                ergebnis.fehler.append(f"Fehler bei {dateipfad}: {str(e)}")

    ergebnis.akten = list(akten_dict.values())

    return ergebnis


def get_pdf_seitenanzahl(pdf_file: BinaryIO) -> int:
    """Ermittelt die Seitenanzahl eines PDFs."""
    if not PYPDF_AVAILABLE:
        return 0

    try:
        pdf_file.seek(0)
        reader = PdfReader(pdf_file)
        return len(reader.pages)
    except:
        return 0


def ist_pdf_verfuegbar() -> bool:
    """Prueft ob PDF-Verarbeitung verfuegbar ist."""
    return PYPDF_AVAILABLE


def ist_pdfplumber_verfuegbar() -> bool:
    """Prueft ob pdfplumber fuer Textextraktion verfuegbar ist."""
    return PDFPLUMBER_AVAILABLE
