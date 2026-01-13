"""
Benutzerverwaltung - Benutzer erstellen, bearbeiten, loeschen
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, List, Optional
import hashlib
import secrets


def render_benutzerverwaltung():
    """Rendert die Benutzerverwaltungsseite"""
    st.header("Benutzerverwaltung")

    # Tabs fuer verschiedene Aktionen
    tab1, tab2, tab3, tab4 = st.tabs([
        "Benutzeruebersicht",
        "Neuer Benutzer",
        "Rollen & Berechtigungen",
        "Audit-Log"
    ])

    with tab1:
        render_benutzer_liste()

    with tab2:
        render_neuer_benutzer()

    with tab3:
        render_rollen_verwaltung()

    with tab4:
        render_audit_log()


def render_benutzer_liste():
    """Zeigt alle Benutzer mit Such- und Filterfunktion"""
    st.subheader("Alle Benutzer")

    # Such- und Filterbereich
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        suchbegriff = st.text_input(
            "Suche",
            placeholder="Name, E-Mail oder Benutzername...",
            label_visibility="collapsed"
        )

    with col2:
        filter_rolle = st.selectbox(
            "Rolle",
            ["Alle", "Admin", "Anwalt", "Mitarbeiter", "Mandant"],
            label_visibility="collapsed"
        )

    with col3:
        filter_status = st.selectbox(
            "Status",
            ["Alle", "Aktiv", "Inaktiv", "Gesperrt"],
            label_visibility="collapsed"
        )

    # Demo-Benutzer
    benutzer = get_demo_benutzer()

    # Filtern
    if suchbegriff:
        suchbegriff_lower = suchbegriff.lower()
        benutzer = [
            b for b in benutzer
            if suchbegriff_lower in b["name"].lower()
            or suchbegriff_lower in b["email"].lower()
            or suchbegriff_lower in b["benutzername"].lower()
        ]

    if filter_rolle != "Alle":
        benutzer = [b for b in benutzer if b["rolle"] == filter_rolle]

    if filter_status != "Alle":
        benutzer = [b for b in benutzer if b["status"] == filter_status]

    st.markdown("---")

    # Statistik
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gesamt", len(benutzer))
    with col2:
        aktiv = len([b for b in benutzer if b["status"] == "Aktiv"])
        st.metric("Aktiv", aktiv)
    with col3:
        inaktiv = len([b for b in benutzer if b["status"] == "Inaktiv"])
        st.metric("Inaktiv", inaktiv)
    with col4:
        gesperrt = len([b for b in benutzer if b["status"] == "Gesperrt"])
        st.metric("Gesperrt", gesperrt)

    st.markdown("---")

    # Benutzerliste
    if benutzer:
        # Header
        header_cols = st.columns([2, 2, 1, 1, 1, 1.5])
        with header_cols[0]:
            st.markdown("**Name**")
        with header_cols[1]:
            st.markdown("**E-Mail**")
        with header_cols[2]:
            st.markdown("**Rolle**")
        with header_cols[3]:
            st.markdown("**Status**")
        with header_cols[4]:
            st.markdown("**Letzter Login**")
        with header_cols[5]:
            st.markdown("**Aktionen**")

        st.markdown("---")

        for user in benutzer:
            cols = st.columns([2, 2, 1, 1, 1, 1.5])

            with cols[0]:
                st.write(user["name"])
                st.caption(f"@{user['benutzername']}")

            with cols[1]:
                st.write(user["email"])

            with cols[2]:
                if user["rolle"] == "Admin":
                    st.error(user["rolle"])
                elif user["rolle"] == "Anwalt":
                    st.warning(user["rolle"])
                elif user["rolle"] == "Mitarbeiter":
                    st.info(user["rolle"])
                else:
                    st.success(user["rolle"])

            with cols[3]:
                if user["status"] == "Aktiv":
                    st.success(user["status"])
                elif user["status"] == "Inaktiv":
                    st.warning(user["status"])
                else:
                    st.error(user["status"])

            with cols[4]:
                st.caption(user["letzter_login"])

            with cols[5]:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("Bearbeiten", key=f"edit_{user['id']}", use_container_width=True):
                        st.session_state.edit_user = user
                        st.rerun()

                with btn_col2:
                    if user["status"] == "Aktiv":
                        if st.button("Sperren", key=f"lock_{user['id']}", use_container_width=True):
                            st.warning(f"Benutzer {user['name']} wurde gesperrt.")
                    else:
                        if st.button("Entsperren", key=f"unlock_{user['id']}", use_container_width=True):
                            st.success(f"Benutzer {user['name']} wurde entsperrt.")

            st.markdown("---")

        # Benutzer bearbeiten Modal
        if st.session_state.get("edit_user"):
            render_benutzer_bearbeiten(st.session_state.edit_user)

    else:
        st.info("Keine Benutzer gefunden.")


def render_benutzer_bearbeiten(user: Dict):
    """Formular zum Bearbeiten eines Benutzers"""
    st.markdown("---")
    st.subheader(f"Benutzer bearbeiten: {user['name']}")

    col1, col2 = st.columns(2)

    with col1:
        vorname = st.text_input("Vorname", value=user["name"].split()[0])
        nachname = st.text_input("Nachname", value=user["name"].split()[-1])
        email = st.text_input("E-Mail", value=user["email"])

    with col2:
        rolle = st.selectbox(
            "Rolle",
            ["Admin", "Anwalt", "Mitarbeiter", "Mandant"],
            index=["Admin", "Anwalt", "Mitarbeiter", "Mandant"].index(user["rolle"])
        )
        status = st.selectbox(
            "Status",
            ["Aktiv", "Inaktiv", "Gesperrt"],
            index=["Aktiv", "Inaktiv", "Gesperrt"].index(user["status"])
        )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Speichern", type="primary", use_container_width=True):
            st.success(f"Benutzer {vorname} {nachname} wurde aktualisiert.")
            st.session_state.edit_user = None
            st.rerun()

    with col2:
        if st.button("Passwort zuruecksetzen", use_container_width=True):
            neues_pw = generate_temp_password()
            st.info(f"Temporaeres Passwort: **{neues_pw}**")

    with col3:
        if st.button("Abbrechen", use_container_width=True):
            st.session_state.edit_user = None
            st.rerun()


def render_neuer_benutzer():
    """Formular zum Erstellen eines neuen Benutzers"""
    st.subheader("Neuen Benutzer anlegen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Persoenliche Daten")

        anrede = st.selectbox("Anrede", ["Herr", "Frau", "Divers"])
        titel = st.text_input("Titel (optional)", placeholder="z.B. Dr., Prof.")
        vorname = st.text_input("Vorname", key="new_vorname")
        nachname = st.text_input("Nachname", key="new_nachname")
        email = st.text_input("E-Mail", key="new_email")
        telefon = st.text_input("Telefon (optional)", key="new_telefon")

    with col2:
        st.markdown("#### Zugangsdaten")

        benutzername = st.text_input(
            "Benutzername",
            value=f"{vorname.lower()}.{nachname.lower()}" if vorname and nachname else "",
            key="new_username"
        )

        rolle = st.selectbox(
            "Rolle",
            ["Anwalt", "Mitarbeiter", "Mandant", "Admin"],
            key="new_rolle"
        )

        # Rollenspezifische Optionen
        if rolle == "Anwalt":
            st.markdown("##### Anwalts-Optionen")
            fachanwalt = st.checkbox("Fachanwalt fuer Familienrecht")
            kanzlei_partner = st.checkbox("Kanzleipartner")

        elif rolle == "Mitarbeiter":
            st.markdown("##### Mitarbeiter-Optionen")
            abteilung = st.selectbox(
                "Abteilung",
                ["Sekretariat", "Buchhaltung", "Empfang", "Sachbearbeitung"]
            )

        elif rolle == "Mandant":
            st.markdown("##### Mandanten-Optionen")
            zugeordnete_akte = st.text_input(
                "Aktenzeichen (optional)",
                placeholder="z.B. 2026/0001"
            )

        st.markdown("##### Passwort")
        passwort_option = st.radio(
            "Passwort-Option",
            ["Automatisch generieren", "Manuell festlegen"],
            horizontal=True
        )

        if passwort_option == "Manuell festlegen":
            passwort = st.text_input("Passwort", type="password", key="new_pw")
            passwort_confirm = st.text_input("Passwort bestaetigen", type="password", key="new_pw_confirm")
        else:
            auto_passwort = generate_temp_password()
            st.info(f"Generiertes Passwort: **{auto_passwort}**")

    st.markdown("---")

    # Berechtigungen
    st.markdown("#### Berechtigungen")

    perm_col1, perm_col2, perm_col3 = st.columns(3)

    with perm_col1:
        st.markdown("**Akten**")
        perm_akten_lesen = st.checkbox("Akten lesen", value=True)
        perm_akten_schreiben = st.checkbox("Akten bearbeiten", value=rolle in ["Anwalt", "Mitarbeiter", "Admin"])
        perm_akten_loeschen = st.checkbox("Akten loeschen", value=rolle in ["Anwalt", "Admin"])

    with perm_col2:
        st.markdown("**Dokumente**")
        perm_dok_lesen = st.checkbox("Dokumente lesen", value=True)
        perm_dok_hochladen = st.checkbox("Dokumente hochladen", value=True)
        perm_dok_loeschen = st.checkbox("Dokumente loeschen", value=rolle in ["Anwalt", "Admin"])

    with perm_col3:
        st.markdown("**Berechnungen**")
        perm_calc_lesen = st.checkbox("Berechnungen ansehen", value=True)
        perm_calc_erstellen = st.checkbox("Berechnungen erstellen", value=rolle in ["Anwalt", "Mitarbeiter", "Admin"])
        perm_calc_freigeben = st.checkbox("Berechnungen freigeben", value=rolle in ["Anwalt", "Admin"])

    st.markdown("---")

    # Benachrichtigungen
    st.markdown("#### Benachrichtigungen")
    notif_col1, notif_col2 = st.columns(2)

    with notif_col1:
        notif_email = st.checkbox("E-Mail-Benachrichtigungen aktivieren", value=True)
        notif_dok = st.checkbox("Bei neuen Dokumenten benachrichtigen", value=True)

    with notif_col2:
        notif_fristen = st.checkbox("Fristenerinnerungen", value=True)
        notif_calc = st.checkbox("Bei neuen Berechnungen benachrichtigen", value=True)

    st.markdown("---")

    # Buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Benutzer anlegen", type="primary", use_container_width=True):
            if vorname and nachname and email and benutzername:
                st.success(f"""
                Benutzer erfolgreich angelegt!

                **Name:** {titel} {vorname} {nachname}
                **E-Mail:** {email}
                **Benutzername:** {benutzername}
                **Rolle:** {rolle}

                Ein Link zur Passworterstellung wurde an {email} gesendet.
                """)
            else:
                st.error("Bitte fuellen Sie alle Pflichtfelder aus.")

    with col2:
        if st.button("Abbrechen", use_container_width=True):
            st.rerun()


def render_rollen_verwaltung():
    """Verwaltung von Rollen und Berechtigungen"""
    st.subheader("Rollen und Berechtigungen")

    # Rollen-Uebersicht
    rollen = {
        "Admin": {
            "beschreibung": "Voller Zugriff auf alle Funktionen inkl. Systemeinstellungen",
            "benutzer": 2,
            "berechtigungen": ["Alle Berechtigungen"]
        },
        "Anwalt": {
            "beschreibung": "Zugriff auf alle Akten und Berechnungen, Freigabe-Berechtigung",
            "benutzer": 4,
            "berechtigungen": [
                "Akten lesen/schreiben/loeschen",
                "Berechnungen erstellen/freigeben",
                "Dokumente verwalten",
                "Mandanten verwalten"
            ]
        },
        "Mitarbeiter": {
            "beschreibung": "Zugriff auf zugewiesene Akten, Berechnungen erstellen",
            "benutzer": 6,
            "berechtigungen": [
                "Akten lesen/schreiben",
                "Berechnungen erstellen",
                "Dokumente hochladen/pruefen"
            ]
        },
        "Mandant": {
            "beschreibung": "Zugriff nur auf eigene Akte(n), Dokumente hochladen",
            "benutzer": 45,
            "berechtigungen": [
                "Eigene Akte(n) lesen",
                "Dokumente hochladen",
                "Freigegebene Berechnungen ansehen"
            ]
        }
    }

    for rolle_name, rolle_data in rollen.items():
        with st.expander(f"**{rolle_name}** ({rolle_data['benutzer']} Benutzer)"):
            st.write(rolle_data["beschreibung"])

            st.markdown("**Berechtigungen:**")
            for berechtigung in rolle_data["berechtigungen"]:
                st.write(f"- {berechtigung}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Berechtigungen bearbeiten", key=f"edit_role_{rolle_name}"):
                    st.info("Berechtigungs-Editor wird geoeffnet...")
            with col2:
                if rolle_name not in ["Admin", "Mandant"]:
                    if st.button(f"Rolle loeschen", key=f"del_role_{rolle_name}"):
                        st.warning("Diese Aktion kann nicht rueckgaengig gemacht werden.")

    st.markdown("---")

    # Neue Rolle erstellen
    st.markdown("#### Neue Rolle erstellen")

    col1, col2 = st.columns(2)

    with col1:
        neue_rolle_name = st.text_input("Rollenname", key="new_role_name")
        neue_rolle_beschreibung = st.text_area("Beschreibung", key="new_role_desc", height=100)

    with col2:
        st.markdown("**Basis-Berechtigungen**")
        basis_rolle = st.selectbox(
            "Berechtigungen kopieren von",
            ["Keine", "Anwalt", "Mitarbeiter", "Mandant"]
        )

    if st.button("Rolle erstellen", type="primary"):
        if neue_rolle_name:
            st.success(f"Rolle '{neue_rolle_name}' wurde erstellt.")
        else:
            st.error("Bitte geben Sie einen Rollennamen ein.")


def render_audit_log():
    """Zeigt Audit-Log fuer Benutzeraktionen"""
    st.subheader("Audit-Log")

    # Filter
    col1, col2, col3 = st.columns(3)

    with col1:
        log_typ = st.selectbox(
            "Ereignistyp",
            ["Alle", "Login", "Benutzer erstellt", "Benutzer geaendert",
             "Passwort geaendert", "Rolle geaendert", "Benutzer gesperrt"]
        )

    with col2:
        log_zeitraum = st.selectbox(
            "Zeitraum",
            ["Heute", "Letzte 7 Tage", "Letzte 30 Tage", "Alle"]
        )

    with col3:
        log_benutzer = st.text_input("Benutzer", placeholder="Nach Benutzer filtern...")

    # Demo Audit-Log
    audit_entries = [
        {
            "zeit": "13.01.2026 14:32:15",
            "benutzer": "Admin",
            "aktion": "Login",
            "details": "Erfolgreich angemeldet von IP 192.168.1.100",
            "status": "success"
        },
        {
            "zeit": "13.01.2026 14:28:00",
            "benutzer": "Admin",
            "aktion": "Benutzer erstellt",
            "details": "Neuer Benutzer: petra.schulz@kanzlei-rhm.de (Mitarbeiter)",
            "status": "success"
        },
        {
            "zeit": "13.01.2026 11:15:30",
            "benutzer": "Admin",
            "aktion": "Passwort zurueckgesetzt",
            "details": "Passwort fuer Benutzer 'wagner' zurueckgesetzt",
            "status": "info"
        },
        {
            "zeit": "12.01.2026 16:45:00",
            "benutzer": "System",
            "aktion": "Benutzer gesperrt",
            "details": "Automatische Sperrung nach 5 fehlgeschlagenen Login-Versuchen: test.user",
            "status": "warning"
        },
        {
            "zeit": "12.01.2026 09:00:00",
            "benutzer": "Admin",
            "aktion": "Rolle geaendert",
            "details": "Benutzer 'heigener': Rolle geaendert von 'Mitarbeiter' zu 'Anwalt'",
            "status": "info"
        },
    ]

    st.markdown("---")

    for entry in audit_entries:
        col1, col2, col3, col4 = st.columns([1.5, 1, 1.5, 3])

        with col1:
            st.caption(entry["zeit"])

        with col2:
            st.write(entry["benutzer"])

        with col3:
            if entry["status"] == "success":
                st.success(entry["aktion"])
            elif entry["status"] == "warning":
                st.warning(entry["aktion"])
            else:
                st.info(entry["aktion"])

        with col4:
            st.caption(entry["details"])

    st.markdown("---")

    # Export-Button
    if st.button("Audit-Log exportieren (CSV)"):
        st.success("Audit-Log wurde als CSV exportiert.")


def get_demo_benutzer() -> List[Dict]:
    """Gibt Demo-Benutzer zurueck"""
    return [
        {
            "id": 1,
            "name": "Administrator",
            "benutzername": "admin",
            "email": "admin@kanzlei-rhm.de",
            "rolle": "Admin",
            "status": "Aktiv",
            "letzter_login": "13.01.2026 14:32"
        },
        {
            "id": 2,
            "name": "Dr. Thomas Mueller",
            "benutzername": "mueller",
            "email": "mueller@kanzlei-rhm.de",
            "rolle": "Anwalt",
            "status": "Aktiv",
            "letzter_login": "13.01.2026 14:15"
        },
        {
            "id": 3,
            "name": "Sabine Heigener",
            "benutzername": "heigener",
            "email": "heigener@kanzlei-rhm.de",
            "rolle": "Anwalt",
            "status": "Aktiv",
            "letzter_login": "13.01.2026 12:30"
        },
        {
            "id": 4,
            "name": "Michael Radtke",
            "benutzername": "radtke",
            "email": "radtke@kanzlei-rhm.de",
            "rolle": "Anwalt",
            "status": "Aktiv",
            "letzter_login": "12.01.2026 17:45"
        },
        {
            "id": 5,
            "name": "Klaus Meier",
            "benutzername": "meier",
            "email": "meier@kanzlei-rhm.de",
            "rolle": "Anwalt",
            "status": "Inaktiv",
            "letzter_login": "05.01.2026 09:00"
        },
        {
            "id": 6,
            "name": "Sandra Schmidt",
            "benutzername": "schmidt",
            "email": "schmidt@kanzlei-rhm.de",
            "rolle": "Mitarbeiter",
            "status": "Aktiv",
            "letzter_login": "13.01.2026 13:45"
        },
        {
            "id": 7,
            "name": "Petra Wagner",
            "benutzername": "wagner",
            "email": "wagner@kanzlei-rhm.de",
            "rolle": "Mitarbeiter",
            "status": "Aktiv",
            "letzter_login": "13.01.2026 11:20"
        },
        {
            "id": 8,
            "name": "Max Mustermann",
            "benutzername": "mandant_mustermann",
            "email": "max.mustermann@email.de",
            "rolle": "Mandant",
            "status": "Aktiv",
            "letzter_login": "12.01.2026 15:30"
        },
        {
            "id": 9,
            "name": "Maria Schmidt",
            "benutzername": "mandant_schmidt",
            "email": "maria.schmidt@email.de",
            "rolle": "Mandant",
            "status": "Aktiv",
            "letzter_login": "11.01.2026 10:00"
        },
    ]


def generate_temp_password() -> str:
    """Generiert ein temporaeres Passwort"""
    import string
    import random
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(chars) for _ in range(12))
