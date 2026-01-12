"""
FamilyKom - Versionsverwaltung

Automatische Versionsnummer basierend auf Datum und Uhrzeit der letzten Aenderung.
Format: YYYY.MM.DD.HHMM
"""

from datetime import datetime

# Letzte Aenderung - wird bei jedem Update aktualisiert
LAST_UPDATE = "2026-01-12 20:45:00"

# Hauptversion
MAJOR_VERSION = 1
MINOR_VERSION = 0

def get_version() -> str:
    """Gibt die vollstaendige Versionsnummer zurueck"""
    try:
        dt = datetime.strptime(LAST_UPDATE, "%Y-%m-%d %H:%M:%S")
        build = dt.strftime("%Y%m%d.%H%M")
        return f"{MAJOR_VERSION}.{MINOR_VERSION}.{build}"
    except ValueError:
        return f"{MAJOR_VERSION}.{MINOR_VERSION}.0"


def get_version_display() -> str:
    """Gibt eine lesbare Versionsanzeige zurueck"""
    try:
        dt = datetime.strptime(LAST_UPDATE, "%Y-%m-%d %H:%M:%S")
        date_str = dt.strftime("%d.%m.%Y")
        time_str = dt.strftime("%H:%M")
        return f"v{MAJOR_VERSION}.{MINOR_VERSION} | Stand: {date_str} {time_str} Uhr"
    except ValueError:
        return f"v{MAJOR_VERSION}.{MINOR_VERSION}"


def get_last_update_datetime() -> datetime:
    """Gibt das Datum der letzten Aenderung als datetime zurueck"""
    try:
        return datetime.strptime(LAST_UPDATE, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.now()


# Aenderungsprotokoll
CHANGELOG = [
    {
        "version": "1.0.20260112.2015",
        "datum": "12.01.2026",
        "aenderungen": [
            "Umfangreiches Dokumentenmanagement pro Akte implementiert",
            "Dokumenten-Approval-Workflow (In Ordnung / Nachbesserung / Abgelehnt)",
            "Gehaltsabrechnungs-Tab mit OCR-Auswertung und Korrekturmoeglichkeit",
            "Berechnungsversionierung mit Zeitstempel und Freitext-Notizen",
            "Aktendetailansicht mit 5 Tabs (Dokumente, Berechnungen, Gehaltsabrechnungen, Schriftsaetze, Historie)",
            "Import von OCR-Daten in Berechnungen",
            "Freigabe von Berechnungen fuer Mandanten",
            "Vollstaendige Aktenhistorie mit allen Aktionen",
        ]
    },
    {
        "version": "1.0.20260112.1830",
        "datum": "12.01.2026",
        "aenderungen": [
            "Datenbankschema erweitert gemaess Pflichtenheft",
            "Neue Tabellen: invitations, case_memberships, request_slots, drafts, approvals",
            "Neue Tabellen: rulesets, court_olg_mapping, ocr_queue, payslip_extractions",
            "Calculation Engine Modul mit Versionierung implementiert",
            "Kindesunterhalt-Rechner mit vollstaendiger Schrittdokumentation",
            "Ehegattenunterhalt-Rechner mit Differenzmethode und Erwerbstaetigenbonus",
            "Zugewinnausgleich-Rechner mit VPI-Indexierung",
            "RVG-Gebuehrenrechner nach Anlage 2 zu § 13 RVG",
            "OLG-Jurisdiktionslogik fuer Schleswig-Holstein",
            "Ruleset-Manager fuer OLG-Leitlinien und Duesseldorfer Tabelle",
        ]
    },
    {
        "version": "1.0.20260112.1645",
        "datum": "12.01.2026",
        "aenderungen": [
            "Vollstaendige Aktenuebersicht mit Such- und Filterfunktion",
            "Umfangreiches Formular fuer neue Akten (4 Tabs)",
            "Dokumentenverwaltung mit Upload und OCR-Suche",
            "Schriftsatzvorlagen und -erstellung",
            "Nachrichtensystem fuer Mandanten",
            "Admin: Benutzerverwaltung mit Rollen und Rechten",
            "Admin: Tabellen-Updates (Duesseldorfer Tabelle, OLG-Leitlinien)",
            "Admin: Systemueberwachung mit Logs und Speicheranalyse",
            "Versionsnummer mit Datum/Uhrzeit eingefuehrt",
        ]
    },
    {
        "version": "1.0.20260112.1530",
        "datum": "12.01.2026",
        "aenderungen": [
            "Dokumentenanforderungssystem fuer Anwaelte implementiert",
            "Mandanten-Upload-Bereich mit prominenten Benachrichtigungen",
            "API-Einstellungen fuer Supabase, Upstash und KI-Dienste",
            "Demo-Zugaenge fuer Anwalt, Mitarbeiter, Mandant und Admin",
        ]
    },
    {
        "version": "1.0.20260110.0900",
        "datum": "10.01.2026",
        "aenderungen": [
            "Initiale Version",
            "Kindesunterhalt-Rechner (Duesseldorfer Tabelle 2025)",
            "Ehegattenunterhalt-Rechner",
            "Zugewinnausgleich-Rechner mit VPI-Indexierung",
            "RVG-Gebuehrenrechner",
        ]
    },
]
