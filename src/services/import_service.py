"""
Import-Service fuer FamilyKom

Bietet echte Import-Funktionalitaet fuer:
- PDF-Dateien mit Lesezeichen-Extraktion (nach NotarKom-Methode)
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

# PDF-Bibliotheken - PyPDF2 (funktioniert wie in NotarKom)
try:
    from PyPDF2 import PdfReader, PdfWriter
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
    gegnervertreter: str = ""
    typ: str = ""
    angelegt: str = ""
    dokumente: List[str] = field(default_factory=list)
    dokument_count: int = 0
    quelle: str = ""
    gegenstandswert: str = ""
    gericht: str = ""
    gerichts_az: str = ""
    # Vollstaendige Adressdaten
    mandant_adresse: Dict = field(default_factory=dict)
    gegner_adresse: Dict = field(default_factory=dict)
    gegnervertreter_adresse: Dict = field(default_factory=dict)


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
    r'([A-ZÄÖÜ][a-zäöüß]+),\s*([A-ZÄÖÜ][a-zäöüß]+)\s*\.?/?\.?\s*([A-ZÄÖÜ][a-zäöüß]+),\s*([A-ZÄÖÜ][a-zäöüß]+)',
    r'Antragsteller(?:in)?:\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)',
    r'Antragsgegner(?:in)?:\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)',
]


def parse_aktenvorblatt(text: str) -> Dict:
    """
    Parst ein RA-Micro Aktenvorblatt und extrahiert alle relevanten Daten.

    Das Aktenvorblatt enthaelt typischerweise:
    - Aktennr.: (z.B. 1263/25)
    - AUFTRAGGEBER: (Mandant mit Adresse)
    - GEGNER: (Gegner mit Adresse)
    - GEGNERVERTRETER: (Anwalt des Gegners)
    - GEGENSTANDSWERT:
    - I. Instanz: (Gericht)

    Args:
        text: Der extrahierte Text des Aktenvorblatts

    Returns:
        Dictionary mit allen extrahierten Daten
    """
    result = {
        'aktenzeichen': None,
        'mandant': None,
        'mandant_adresse': {},
        'gegner': None,
        'gegner_adresse': {},
        'gegnervertreter': None,
        'gegnervertreter_adresse': {},
        'gegenstandswert': None,
        'gericht': None,
        'gerichts_az': None,
        'referat': None,
        'sachbearbeiter': None
    }

    # Aktenzeichen / Aktennr.
    az_match = re.search(r'Aktennr\.?:?\s*(\d+[/-]\d+)', text)
    if az_match:
        result['aktenzeichen'] = az_match.group(1)

    # Gegenstandswert
    gw_match = re.search(r'GEGENSTANDSWERT:?\s*([\d.,]+)\s*(?:EUR|€)?', text, re.IGNORECASE)
    if gw_match:
        result['gegenstandswert'] = gw_match.group(1).strip()

    # Gericht (I. Instanz)
    gericht_match = re.search(r'I\.\s*Instanz:?\s*([A-Za-zäöüÄÖÜß\s]+?)(?:Aktenzeichen|II\.|$)', text)
    if gericht_match:
        result['gericht'] = gericht_match.group(1).strip()

    # Gerichtsaktenzeichen
    gaz_match = re.search(r'Aktenzeichen:?\s*(\d+\s*[A-Z]+\s*\d+[/-]\d+)', text)
    if gaz_match:
        result['gerichts_az'] = gaz_match.group(1).strip()

    # Referat/SB
    ref_match = re.search(r'SB\s*/\s*Referat:?\s*([A-Za-z0-9/]+)', text)
    if ref_match:
        result['referat'] = ref_match.group(1).strip()

    # AUFTRAGGEBER (Mandant) - komplexeres Parsing
    auftraggeber_section = extract_section(text, 'AUFTRAGGEBER', ['GEGNERVERTRETER', 'GEGNER', 'RECHTSSCHUTZ'])
    if auftraggeber_section:
        mandant_data = parse_party_section(auftraggeber_section)
        result['mandant'] = mandant_data.get('name', '')
        result['mandant_adresse'] = mandant_data

    # GEGNER
    gegner_section = extract_section(text, 'GEGNER:', ['AUFTRAGGEBER', 'GEGNERVERTRETER', 'RECHTSSCHUTZ'])
    if not gegner_section:
        # Alternative ohne Doppelpunkt
        gegner_section = extract_section(text, '\nGEGNER', ['AUFTRAGGEBER', 'GEGNERVERTRETER', 'RECHTSSCHUTZ'])
    if gegner_section:
        gegner_data = parse_party_section(gegner_section)
        result['gegner'] = gegner_data.get('name', '')
        result['gegner_adresse'] = gegner_data

    # GEGNERVERTRETER
    gv_section = extract_section(text, 'GEGNERVERTRETER', ['AUFTRAGGEBER', 'GEGNER:', 'RECHTSSCHUTZ'])
    if gv_section:
        gv_data = parse_party_section(gv_section)
        result['gegnervertreter'] = gv_data.get('name', '')
        result['gegnervertreter_adresse'] = gv_data

    return result


def extract_section(text: str, start_marker: str, end_markers: List[str]) -> Optional[str]:
    """
    Extrahiert einen Textabschnitt zwischen einem Start-Marker und moeglichen End-Markern.

    Args:
        text: Der Gesamttext
        start_marker: Der Beginn des Abschnitts
        end_markers: Liste moeglicher End-Marker

    Returns:
        Der extrahierte Textabschnitt oder None
    """
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return None

    # Start nach dem Marker
    section_start = start_idx + len(start_marker)

    # Finde den naechsten End-Marker
    end_idx = len(text)
    for marker in end_markers:
        marker_idx = text.find(marker, section_start)
        if marker_idx != -1 and marker_idx < end_idx:
            end_idx = marker_idx

    section = text[section_start:end_idx].strip()
    return section if section else None


def parse_party_section(section: str) -> Dict:
    """
    Parst einen Abschnitt mit Parteidaten (Name, Adresse, Kontakt).

    Args:
        section: Der Textabschnitt

    Returns:
        Dictionary mit Name, Strasse, PLZ, Ort, Tel, Email, etc.
    """
    result = {
        'name': '',
        'strasse': '',
        'plz': '',
        'ort': '',
        'telefon': '',
        'fax': '',
        'email': '',
        'mobil': '',
        'adressnr': ''
    }

    lines = [l.strip() for l in section.split('\n') if l.strip()]

    # Adressnr. extrahieren
    adressnr_match = re.search(r'Adressnr\.?:?\s*(\d+)', section)
    if adressnr_match:
        result['adressnr'] = adressnr_match.group(1)

    # Kontaktdaten extrahieren
    tel_match = re.search(r'Tel\d?:?\s*([\d\s/\-]+)', section)
    if tel_match:
        result['telefon'] = tel_match.group(1).strip()

    mobil_match = re.search(r'Mobil:?\s*([\d\s/\-]+)', section)
    if mobil_match:
        result['mobil'] = mobil_match.group(1).strip()

    fax_match = re.search(r'Fax:?\s*([\d\s/\-]+)', section)
    if fax_match:
        result['fax'] = fax_match.group(1).strip()

    email_match = re.search(r'E-Mail:?\s*([^\s]+@[^\s]+)', section)
    if email_match:
        result['email'] = email_match.group(1).strip()

    # PLZ und Ort
    plz_ort_match = re.search(r'(\d{5})\s+([A-Za-zäöüÄÖÜß\s\-]+?)(?:\n|Tel|Fax|E-Mail|$)', section)
    if plz_ort_match:
        result['plz'] = plz_ort_match.group(1)
        result['ort'] = plz_ort_match.group(2).strip()

    # Name und Adresse - die ersten Zeilen ohne Kontaktdaten
    name_lines = []
    for line in lines:
        # Zeilen mit Kontaktdaten ueberspringen
        if any(marker in line for marker in ['Tel:', 'Tel1:', 'Tel2:', 'Fax:', 'E-Mail:', 'Mobil:', 'Adressnr', 'geb.:']):
            continue
        # PLZ-Zeile ueberspringen
        if re.match(r'^\d{5}\s', line):
            continue
        # Leere Adressnr-Zeile ueberspringen
        if re.match(r'^Adressnr', line):
            continue
        name_lines.append(line)

    if name_lines:
        # Erste Zeile ist oft der Name
        result['name'] = name_lines[0]

        # Zweite Zeile ist oft die Strasse
        if len(name_lines) > 1:
            # Pruefen ob es eine Firma + Person ist
            if any(x in name_lines[0] for x in ['GmbH', 'mbH', 'AG', 'KG', 'OHG', 'e.V.']):
                # Firma + ggf. Ansprechpartner
                if len(name_lines) > 1 and ('Frau' in name_lines[1] or 'Herr' in name_lines[1]):
                    result['name'] = name_lines[0] + ', ' + name_lines[1]
                    if len(name_lines) > 2:
                        result['strasse'] = name_lines[2]
                else:
                    result['strasse'] = name_lines[1]
            else:
                result['strasse'] = name_lines[1]

    return result


def ist_aktenvorblatt(text: str, bookmark_name: str = "") -> bool:
    """
    Prueft ob ein Text/Bookmark ein Aktenvorblatt ist.

    Args:
        text: Der Text der Seite
        bookmark_name: Der Name des Lesezeichens

    Returns:
        True wenn es sich um ein Aktenvorblatt handelt
    """
    # Nach Lesezeichen-Namen pruefen
    if bookmark_name:
        bm_lower = bookmark_name.lower()
        if 'aktenvorblatt' in bm_lower or 'deckblatt' in bm_lower:
            return True

    # Nach typischen Aktenvorblatt-Inhalten pruefen
    indicators = [
        'Aktennr.:',
        'AUFTRAGGEBER:',
        'GEGNER:',
        'GEGENSTANDSWERT:',
        'I. Instanz:',
        'FRISTEN/WIEDERVORLAGEN',
        'TERMINE:'
    ]

    matches = sum(1 for ind in indicators if ind in text)
    return matches >= 3  # Mindestens 3 Indikatoren gefunden


def extract_documents_from_bookmarks(pdf_reader, num_pages) -> List[Dict]:
    """
    Extrahiert Dokumente aus PDF-Lesezeichen (Bookmarks/Outlines).
    Nach der funktionierenden NotarKom-Methode.

    Args:
        pdf_reader: PdfReader-Objekt
        num_pages: Gesamtseitenzahl des PDFs

    Returns:
        Liste von Dokumenten mit name, start_page, end_page
    """
    try:
        outlines = pdf_reader.outline
        if not outlines:
            return []

        # Bookmarks rekursiv flach extrahieren
        flat_bookmarks = []

        def walk_outlines(items):
            for item in items:
                if isinstance(item, list):
                    walk_outlines(item)  # Rekursiv bei verschachtelten Bookmarks
                else:
                    try:
                        title = getattr(item, 'title', None) or str(item)
                        # Wichtig: get_destination_page_number statt get_page_number!
                        page_idx = pdf_reader.get_destination_page_number(item)
                        if title and page_idx is not None:
                            flat_bookmarks.append((title.strip(), page_idx))
                    except Exception as e:
                        print(f"Fehler bei Bookmark: {e}")
                        continue

        walk_outlines(outlines)

        if not flat_bookmarks:
            return []

        # Nach Seitennummer sortieren und Duplikate entfernen
        flat_bookmarks = sorted(set(flat_bookmarks), key=lambda x: x[1])

        print(f"Gefundene Bookmarks: {len(flat_bookmarks)}")
        for title, page in flat_bookmarks[:5]:  # Debug: erste 5 zeigen
            print(f"  - '{title}' auf Seite {page + 1}")

        # Dokumente mit Start- und End-Seiten erstellen
        documents = []
        for idx, (title, start_idx) in enumerate(flat_bookmarks):
            start_page = start_idx + 1  # 1-basiert

            # End-Seite = Seite vor dem naechsten Bookmark
            if idx + 1 < len(flat_bookmarks):
                end_page = flat_bookmarks[idx + 1][1]
            else:
                end_page = num_pages

            documents.append({
                'name': title,
                'start_page': start_page,
                'end_page': end_page,
            })

        return documents

    except Exception as e:
        print(f"Fehler beim Extrahieren der Bookmarks: {e}")
        import traceback
        traceback.print_exc()
        return []


def split_pdf_by_pages(pdf_bytes: bytes, start_page: int, end_page: int) -> bytes:
    """
    Extrahiert einen Seitenbereich als eigenes PDF.

    Args:
        pdf_bytes: Original-PDF als Bytes
        start_page: Startseite (1-basiert)
        end_page: Endseite (1-basiert, inklusiv)

    Returns:
        bytes: Extrahiertes PDF als Bytes
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    # Seiten kopieren (0-basiert)
    for page_num in range(start_page - 1, end_page):
        if page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()


def extrahiere_lesezeichen_aus_pdf(pdf_file: BinaryIO) -> List[Lesezeichen]:
    """
    Extrahiert alle Lesezeichen (Bookmarks) aus einem PDF.
    Verwendet die NotarKom-Methode mit get_destination_page_number.

    Args:
        pdf_file: PDF-Datei als Binary-Stream

    Returns:
        Liste von Lesezeichen-Objekten
    """
    if not PYPDF_AVAILABLE:
        print("PyPDF2 nicht verfuegbar")
        return []

    lesezeichen_liste = []

    try:
        # Dateiposition zuruecksetzen - wichtig bei Streamlit file_uploader!
        pdf_file.seek(0)
        reader = PdfReader(pdf_file)
        num_pages = len(reader.pages)

        # NotarKom-Methode verwenden
        documents = extract_documents_from_bookmarks(reader, num_pages)

        # In Lesezeichen-Objekte konvertieren
        for doc in documents:
            lz = Lesezeichen(
                titel=doc['name'],
                seite=doc['start_page'],
                ebene=1
            )
            lesezeichen_liste.append(lz)

        if lesezeichen_liste:
            print(f"Insgesamt {len(lesezeichen_liste)} Lesezeichen extrahiert")
        else:
            print("Keine Lesezeichen im PDF gefunden")
            print(f"PDF hat {num_pages} Seiten")

    except Exception as e:
        print(f"Fehler beim Lesen der Lesezeichen: {e}")
        import traceback
        traceback.print_exc()

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

    # Zuerst pdfplumber versuchen (bessere Textextraktion)
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

    # Fallback auf PyPDF2
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
            print(f"PyPDF2 Fehler: {e}")

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
    Verwendet die NotarKom split_pdf_by_pages Methode.

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
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)

        reader = PdfReader(io.BytesIO(pdf_bytes))
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
            start_page = lz.seite  # 1-basiert

            # Ende ist entweder naechstes Lesezeichen oder Ende des Dokuments
            if i + 1 < len(relevante_lz):
                end_page = relevante_lz[i + 1].seite - 1
            else:
                end_page = total_pages

            # PDF-Teil extrahieren mit NotarKom-Methode
            doc_pdf_bytes = split_pdf_by_pages(pdf_bytes, start_page, end_page)

            # Dateiname aus Lesezeichen-Titel erstellen
            safe_name = re.sub(r'[^\w\s-]', '', lz.titel)
            safe_name = re.sub(r'\s+', '_', safe_name)
            if not safe_name:
                safe_name = f"Dokument_{i+1}"

            dokument = ExtrahiertesDokument(
                name=f"{safe_name}.pdf",
                start_seite=start_page,
                end_seite=end_page,
                seitenanzahl=end_page - start_page + 1,
                pdf_bytes=doc_pdf_bytes,
                text_vorschau=lz.titel
            )
            dokumente.append(dokument)

    except Exception as e:
        print(f"Fehler beim Teilen des PDFs: {e}")
        import traceback
        traceback.print_exc()

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


def parse_ra_micro_pdf(pdf_file: BinaryIO) -> Dict:
    """
    Parst eine RA-Micro Gesamt-PDF.
    Sucht speziell nach dem Aktenvorblatt um alle Beteiligtendaten zu extrahieren.

    Args:
        pdf_file: PDF-Datei als Binary-Stream

    Returns:
        Dictionary mit Parsing-Ergebnissen
    """
    pdf_file.seek(0)
    pdf_reader = PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)

    # 1. Dokumente/Lesezeichen aus PDF extrahieren
    documents = extract_documents_from_bookmarks(pdf_reader, num_pages)

    # Fallback wenn keine Lesezeichen
    if not documents:
        documents = [{
            'name': 'Gesamtakte',
            'start_page': 1,
            'end_page': num_pages
        }]

    # 2. Aktenvorblatt suchen und parsen
    aktenvorblatt_data = None
    aktenvorblatt_text = ""

    # Zuerst in Lesezeichen nach "Aktenvorblatt" suchen
    for doc in documents:
        doc_name_lower = doc['name'].lower()
        if 'aktenvorblatt' in doc_name_lower or 'deckblatt' in doc_name_lower:
            # Text der Aktenvorblatt-Seite(n) extrahieren
            start_idx = doc['start_page'] - 1  # 0-basiert
            end_idx = min(doc.get('end_page', start_idx + 1), start_idx + 3)  # Max 3 Seiten

            for page_idx in range(start_idx, end_idx):
                if page_idx < num_pages:
                    page_text = pdf_reader.pages[page_idx].extract_text() or ""
                    aktenvorblatt_text += page_text + "\n"

            if aktenvorblatt_text:
                print(f"Aktenvorblatt gefunden bei Lesezeichen: {doc['name']}")
                aktenvorblatt_data = parse_aktenvorblatt(aktenvorblatt_text)
            break

    # Falls kein Aktenvorblatt-Lesezeichen, erste Seiten auf Aktenvorblatt pruefen
    if not aktenvorblatt_data:
        for page_idx in range(min(5, num_pages)):  # Erste 5 Seiten pruefen
            page_text = pdf_reader.pages[page_idx].extract_text() or ""
            if ist_aktenvorblatt(page_text):
                print(f"Aktenvorblatt gefunden auf Seite {page_idx + 1}")
                # Auch Folgeseite mit einbeziehen (Aktenvorblatt kann 2 Seiten sein)
                if page_idx + 1 < num_pages:
                    page_text += "\n" + (pdf_reader.pages[page_idx + 1].extract_text() or "")
                aktenvorblatt_text = page_text
                aktenvorblatt_data = parse_aktenvorblatt(page_text)
                break

    # 3. Fallback: Allgemeine Textextraktion
    if not aktenvorblatt_data:
        full_text = ""
        for page in pdf_reader.pages[:10]:  # Erste 10 Seiten
            full_text += (page.extract_text() or "") + "\n"

        # Alte Methode als Fallback
        aktenzeichen = erkenne_aktenzeichen(full_text)
        mandant, gegner = erkenne_parteien(full_text)
        verfahrensart = erkenne_verfahrensart(full_text)

        return {
            'success': True,
            'aktenzeichen': aktenzeichen,
            'mandant': mandant,
            'gegner': gegner,
            'gegnervertreter': None,
            'mandant_adresse': {},
            'gegner_adresse': {},
            'gegnervertreter_adresse': {},
            'gegenstandswert': None,
            'gericht': None,
            'gerichts_az': None,
            'verfahrensart': verfahrensart,
            'documents': documents,
            'num_pages': num_pages,
            'aktenvorblatt_gefunden': False
        }

    # Verfahrensart aus Gesamttext bestimmen
    full_text = aktenvorblatt_text
    for page in pdf_reader.pages[:5]:
        full_text += (page.extract_text() or "") + "\n"
    verfahrensart = erkenne_verfahrensart(full_text)

    # Debug-Ausgabe
    print(f"Aktenvorblatt-Daten extrahiert:")
    print(f"  Aktenzeichen: {aktenvorblatt_data.get('aktenzeichen')}")
    print(f"  Mandant: {aktenvorblatt_data.get('mandant')}")
    print(f"  Gegner: {aktenvorblatt_data.get('gegner')}")
    print(f"  Gegnervertreter: {aktenvorblatt_data.get('gegnervertreter')}")
    print(f"  Gericht: {aktenvorblatt_data.get('gericht')}")

    return {
        'success': True,
        'aktenzeichen': aktenvorblatt_data.get('aktenzeichen'),
        'mandant': aktenvorblatt_data.get('mandant'),
        'gegner': aktenvorblatt_data.get('gegner'),
        'gegnervertreter': aktenvorblatt_data.get('gegnervertreter'),
        'mandant_adresse': aktenvorblatt_data.get('mandant_adresse', {}),
        'gegner_adresse': aktenvorblatt_data.get('gegner_adresse', {}),
        'gegnervertreter_adresse': aktenvorblatt_data.get('gegnervertreter_adresse', {}),
        'gegenstandswert': aktenvorblatt_data.get('gegenstandswert'),
        'gericht': aktenvorblatt_data.get('gericht'),
        'gerichts_az': aktenvorblatt_data.get('gerichts_az'),
        'verfahrensart': verfahrensart,
        'documents': documents,
        'num_pages': num_pages,
        'aktenvorblatt_gefunden': True
    }


def generiere_aktenzeichen_aus_dateiname(dateiname: str) -> str:
    """
    Generiert ein Aktenzeichen aus dem Dateinamen.

    Args:
        dateiname: Der Dateiname

    Returns:
        Generiertes Aktenzeichen
    """
    # Versuche Aktenzeichen aus Dateiname zu extrahieren
    for muster in AKTENZEICHEN_MUSTER:
        match = re.search(muster, dateiname)
        if match:
            return match.group(1)

    # Fallback: Aus Dateinamen generieren
    # Entferne Erweiterung und Sonderzeichen
    name = os.path.splitext(dateiname)[0]
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name).strip()

    if name:
        # Jahr + bereinigte Dateiname
        jahr = datetime.now().year
        return f"{jahr}/{name[:20]}"
    else:
        # Timestamp-basiert
        return datetime.now().strftime("%Y/%m%d%H%M")


def importiere_pdf(pdf_file: BinaryIO, dateiname: str = "") -> ImportErgebnis:
    """
    Hauptfunktion zum Importieren einer PDF-Datei.
    Verwendet die NotarKom parse_ra_micro_pdf Methode.

    WICHTIG: Erstellt IMMER eine Akte mit den echten PDF-Daten,
    auch wenn kein Aktenzeichen automatisch erkannt wird.

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

    try:
        # NotarKom-Methode verwenden
        pdf_file.seek(0)
        parse_result = parse_ra_micro_pdf(pdf_file)

        # Lesezeichen extrahieren fuer UI
        pdf_file.seek(0)
        lesezeichen = extrahiere_lesezeichen_aus_pdf(pdf_file)
        ergebnis.lesezeichen = lesezeichen

        if parse_result['documents']:
            doc_count = len(parse_result['documents'])
            if doc_count > 1 or parse_result['documents'][0]['name'] != 'Gesamtakte':
                ergebnis.hinweise.append(f"{doc_count} Lesezeichen/Dokumente aus PDF extrahiert")
            else:
                ergebnis.hinweise.append("Keine Lesezeichen im PDF gefunden - Gesamtdokument wird verwendet")

        # Aktenzeichen bestimmen (automatisch oder aus Dateiname)
        aktenzeichen = parse_result.get('aktenzeichen')
        az_quelle = "automatisch erkannt"

        if not aktenzeichen:
            # Versuche Aktenzeichen aus Dateiname zu generieren
            aktenzeichen = generiere_aktenzeichen_aus_dateiname(dateiname)
            az_quelle = "aus Dateiname generiert"
            ergebnis.hinweise.append(f"Aktenzeichen {az_quelle}: {aktenzeichen}")

        # Aktenvorblatt-Hinweis
        if parse_result.get('aktenvorblatt_gefunden'):
            ergebnis.hinweise.append("Aktenvorblatt gefunden - Beteiligte automatisch extrahiert")

        # IMMER eine Akte erstellen mit den echten PDF-Daten
        akte = ErkannteAkte(
            aktenzeichen=aktenzeichen,
            mandant=parse_result.get('mandant') or "Aus PDF importiert",
            gegner=parse_result.get('gegner') or "Siehe Dokumente",
            gegnervertreter=parse_result.get('gegnervertreter') or "",
            typ=parse_result.get('verfahrensart') or "Familienrecht",
            angelegt=datetime.now().strftime("%d.%m.%Y"),
            quelle=f"RA-MICRO Import ({az_quelle})",
            gegenstandswert=parse_result.get('gegenstandswert') or "",
            gericht=parse_result.get('gericht') or "",
            gerichts_az=parse_result.get('gerichts_az') or "",
            mandant_adresse=parse_result.get('mandant_adresse', {}),
            gegner_adresse=parse_result.get('gegner_adresse', {}),
            gegnervertreter_adresse=parse_result.get('gegnervertreter_adresse', {})
        )

        # Dokumente aus Lesezeichen - das sind die ECHTEN Dokumentnamen aus dem PDF!
        akte.dokumente = [d['name'] for d in parse_result['documents']]
        akte.dokument_count = len(parse_result['documents'])

        # PDF-Teilung fuer Download vorbereiten
        if lesezeichen:
            pdf_file.seek(0)
            dokumente = teile_pdf_nach_lesezeichen(pdf_file, lesezeichen)
            ergebnis.dokumente = dokumente

        ergebnis.akten.append(akte)

        # Debug-Info
        print(f"Akte erstellt: {aktenzeichen}")
        print(f"  Mandant: {akte.mandant}")
        print(f"  Dokumente: {akte.dokument_count}")
        for doc in akte.dokumente[:5]:
            print(f"    - {doc}")

    except Exception as e:
        ergebnis.erfolgreich = False
        ergebnis.fehler.append(f"Import-Fehler: {str(e)}")
        import traceback
        traceback.print_exc()

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
