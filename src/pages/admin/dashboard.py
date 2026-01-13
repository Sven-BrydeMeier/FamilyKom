"""
Admin Dashboard - Uebersicht und Systemverwaltung
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def render_admin_dashboard():
    """Rendert das Admin-Dashboard mit allen Uebersichten"""
    st.header("Administrator-Dashboard")

    # Statistik-Karten
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Aktive Benutzer",
            get_active_users_count(),
            delta="+2 diese Woche"
        )

    with col2:
        st.metric(
            "Offene Akten",
            get_open_cases_count(),
            delta="+5 diese Woche"
        )

    with col3:
        st.metric(
            "Dokumente heute",
            get_documents_today(),
            delta="+12"
        )

    with col4:
        st.metric(
            "Berechnungen",
            get_calculations_count(),
            delta="+8 diese Woche"
        )

    st.markdown("---")

    # Tabs fuer verschiedene Bereiche
    tab1, tab2, tab3, tab4 = st.tabs([
        "Systemuebersicht",
        "Letzte Aktivitaeten",
        "Auslastung",
        "Warnungen"
    ])

    with tab1:
        render_system_overview()

    with tab2:
        render_recent_activities()

    with tab3:
        render_system_load()

    with tab4:
        render_warnings()


def render_system_overview():
    """Zeigt Systemuebersicht"""
    st.subheader("Systemstatus")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Dienste")

        # Dienst-Status (Demo)
        services = [
            {"name": "Datenbank (Supabase)", "status": "online", "latency": "45ms"},
            {"name": "Cache (Redis)", "status": "online", "latency": "12ms"},
            {"name": "OCR-Service", "status": "online", "latency": "180ms"},
            {"name": "E-Mail-Service", "status": "online", "latency": "95ms"},
            {"name": "PDF-Verarbeitung", "status": "online", "latency": "220ms"},
        ]

        for service in services:
            col_name, col_status, col_latency = st.columns([2, 1, 1])
            with col_name:
                st.write(service["name"])
            with col_status:
                if service["status"] == "online":
                    st.success("Online")
                else:
                    st.error("Offline")
            with col_latency:
                st.caption(service["latency"])

    with col2:
        st.markdown("#### Speichernutzung")

        # Speicher-Info (Demo)
        storage_info = {
            "Dokumente": {"used": 2.4, "total": 10, "unit": "GB"},
            "Datenbank": {"used": 0.8, "total": 5, "unit": "GB"},
            "Cache": {"used": 0.2, "total": 1, "unit": "GB"},
        }

        for name, info in storage_info.items():
            progress = info["used"] / info["total"]
            st.write(f"**{name}:** {info['used']} / {info['total']} {info['unit']}")
            st.progress(progress)

    st.markdown("---")

    # Benutzerstatistiken
    st.markdown("#### Benutzerstatistiken")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Nach Rolle**")
        roles = {
            "Administratoren": 2,
            "Anwaelte": 4,
            "Mitarbeiter": 6,
            "Mandanten": 45
        }
        for role, count in roles.items():
            st.write(f"- {role}: {count}")

    with col2:
        st.markdown("**Heute aktiv**")
        st.write("- Anwaelte: 4")
        st.write("- Mitarbeiter: 5")
        st.write("- Mandanten: 12")

    with col3:
        st.markdown("**Letzte 7 Tage**")
        st.write("- Neue Benutzer: 3")
        st.write("- Deaktiviert: 0")
        st.write("- Passwoerter reset: 1")


def render_recent_activities():
    """Zeigt letzte Aktivitaeten"""
    st.subheader("Letzte Aktivitaeten")

    # Filter
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        activity_filter = st.selectbox(
            "Aktivitaetstyp",
            ["Alle", "Logins", "Dokumente", "Berechnungen", "Akten", "System"],
            label_visibility="collapsed"
        )

    with col2:
        date_filter = st.selectbox(
            "Zeitraum",
            ["Heute", "Letzte 7 Tage", "Letzte 30 Tage"],
            label_visibility="collapsed"
        )

    # Aktivitaeten (Demo)
    activities = [
        {
            "zeit": "14:32",
            "benutzer": "Dr. Mueller",
            "aktion": "Login",
            "details": "Erfolgreich angemeldet",
            "typ": "login"
        },
        {
            "zeit": "14:28",
            "benutzer": "Mandant Schmidt",
            "aktion": "Dokument hochgeladen",
            "details": "Gehaltsabrechnung_Dez2025.pdf",
            "typ": "dokument"
        },
        {
            "zeit": "14:15",
            "benutzer": "Frau Wagner",
            "aktion": "Berechnung erstellt",
            "details": "Kindesunterhalt Az. 2026/0015",
            "typ": "berechnung"
        },
        {
            "zeit": "13:58",
            "benutzer": "RA Heigener",
            "aktion": "Akte angelegt",
            "details": "Az. 2026/0026 - Weber ./. Weber",
            "typ": "akte"
        },
        {
            "zeit": "13:45",
            "benutzer": "System",
            "aktion": "Backup erstellt",
            "details": "Tagessicherung erfolgreich",
            "typ": "system"
        },
        {
            "zeit": "13:30",
            "benutzer": "Admin",
            "aktion": "Benutzer erstellt",
            "details": "Neuer Mitarbeiter: Petra Schulz",
            "typ": "system"
        },
        {
            "zeit": "12:45",
            "benutzer": "Dr. Mueller",
            "aktion": "PDF importiert",
            "details": "RA-MICRO Export (15 Lesezeichen)",
            "typ": "dokument"
        },
    ]

    st.markdown("---")

    for activity in activities:
        col1, col2, col3, col4 = st.columns([0.5, 1.5, 1.5, 2])

        with col1:
            st.caption(activity["zeit"])

        with col2:
            st.write(activity["benutzer"])

        with col3:
            if activity["typ"] == "login":
                st.info(activity["aktion"])
            elif activity["typ"] == "dokument":
                st.success(activity["aktion"])
            elif activity["typ"] == "berechnung":
                st.warning(activity["aktion"])
            elif activity["typ"] == "akte":
                st.success(activity["aktion"])
            else:
                st.info(activity["aktion"])

        with col4:
            st.caption(activity["details"])


def render_system_load():
    """Zeigt Systemauslastung"""
    st.subheader("Systemauslastung")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Server-Ressourcen")

        # CPU
        st.write("**CPU-Auslastung**")
        cpu_usage = 35
        st.progress(cpu_usage / 100)
        st.caption(f"{cpu_usage}% verwendet")

        # RAM
        st.write("**Arbeitsspeicher**")
        ram_usage = 62
        st.progress(ram_usage / 100)
        st.caption(f"{ram_usage}% verwendet (3.1 / 5 GB)")

        # Disk
        st.write("**Festplatte**")
        disk_usage = 45
        st.progress(disk_usage / 100)
        st.caption(f"{disk_usage}% verwendet (45 / 100 GB)")

    with col2:
        st.markdown("#### Anfragen pro Stunde")

        # Simulated hourly data
        hours = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00"]
        requests = [45, 120, 180, 210, 95, 165, 145]

        for hour, count in zip(hours, requests):
            col_h, col_bar = st.columns([0.3, 0.7])
            with col_h:
                st.caption(hour)
            with col_bar:
                bar_width = min(count / 250, 1.0)
                st.progress(bar_width)

    st.markdown("---")

    st.markdown("#### Tagesstatistik")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("API-Aufrufe", "2,458", "+15%")
    with col2:
        st.metric("Durchschn. Antwortzeit", "145ms", "-12ms")
    with col3:
        st.metric("Fehlerrate", "0.2%", "-0.1%")
    with col4:
        st.metric("Cache-Trefferquote", "94%", "+2%")


def render_warnings():
    """Zeigt Systemwarnungen"""
    st.subheader("Warnungen und Hinweise")

    # Warnungen (Demo)
    warnings = [
        {
            "level": "warning",
            "title": "Speicherplatz niedrig",
            "message": "Dokumentenspeicher bei 85% Auslastung. Bereinigung empfohlen.",
            "time": "vor 2 Stunden"
        },
        {
            "level": "info",
            "title": "Backup ausstehend",
            "message": "Woechentliches Vollbackup fuer Sonntag 02:00 geplant.",
            "time": "geplant"
        },
        {
            "level": "success",
            "title": "Sicherheitsupdate installiert",
            "message": "PyPDF2 wurde auf Version 3.0.1 aktualisiert.",
            "time": "vor 1 Tag"
        },
    ]

    for warning in warnings:
        if warning["level"] == "error":
            st.error(f"**{warning['title']}** ({warning['time']})\n\n{warning['message']}")
        elif warning["level"] == "warning":
            st.warning(f"**{warning['title']}** ({warning['time']})\n\n{warning['message']}")
        elif warning["level"] == "info":
            st.info(f"**{warning['title']}** ({warning['time']})\n\n{warning['message']}")
        else:
            st.success(f"**{warning['title']}** ({warning['time']})\n\n{warning['message']}")

    st.markdown("---")

    # Audit-Log Schnellzugriff
    st.markdown("#### Schnellaktionen")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Systemstatus pruefen", use_container_width=True):
            st.success("Alle Systeme funktionieren normal.")

    with col2:
        if st.button("Cache leeren", use_container_width=True):
            st.success("Cache wurde geleert.")

    with col3:
        if st.button("Backup starten", use_container_width=True):
            st.info("Backup wurde in die Warteschlange aufgenommen.")


# Hilfsfunktionen fuer Statistiken (Demo-Daten)
def get_active_users_count() -> int:
    return 57

def get_open_cases_count() -> int:
    return 42

def get_documents_today() -> int:
    return 23

def get_calculations_count() -> int:
    return 156
