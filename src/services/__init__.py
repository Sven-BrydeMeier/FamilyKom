"""
Services fuer FamilyKom

Enthaelt:
- Import-Service (import_service.py) - PDF/ZIP Import-Funktionalitaet
  Verwendet PyPDF2 mit get_destination_page_number (NotarKom-Methode)
- Auth-Service (auth_service.py) - Authentifizierung mit Supabase/Demo
- OCR-Service (ocr_service.py) - Texterkennung aus gescannten Dokumenten
- Email-Service (email_service.py) - E-Mail Benachrichtigungen
"""

from .import_service import (
    importiere_pdf,
    importiere_zip,
    extrahiere_lesezeichen_aus_pdf,
    teile_pdf_nach_lesezeichen,
    extract_documents_from_bookmarks,
    split_pdf_by_pages,
    parse_ra_micro_pdf,
    ist_pdf_verfuegbar,
    ist_pdfplumber_verfuegbar,
    get_pdf_seitenanzahl,
    ErkannteAkte,
    ImportErgebnis,
    Lesezeichen,
    ExtrahiertesDokument
)

from .auth_service import (
    AuthService,
    AuthErgebnis,
    BenutzerRolle,
    erstelle_auth_service
)

from .ocr_service import (
    OCRService,
    OCRErgebnis,
    OCRSprache,
    DokumentTyp,
    SeitenOCR,
    ocr_bild,
    ocr_pdf
)

from .email_service import (
    EmailService,
    EmailNachricht,
    EmailErgebnis,
    EmailAnhang,
    EmailVorlagen,
    EmailPrioritaet,
    EmailTyp,
    erstelle_email_service
)
