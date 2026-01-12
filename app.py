"""
FamilyKom - Familienrechts-Applikation
Hauptanwendung (Streamlit)

Für RHM - Radtke, Heigener und Meier Kanzlei, Rendsburg
"""

import streamlit as st
from datetime import datetime

from config.settings import settings

# Seitenkonfiguration muss zuerst kommen
st.set_page_config(
    page_title="FamilyKom - Familienrecht",
    page_icon="scales",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a Bug": None,
        "About": """
        ## FamilyKom
        Familienrechts-Applikation v1.0

        Entwickelt für RHM - Radtke, Heigener und Meier
        Kanzlei in Rendsburg
        """
    }
)


def init_session_state():
    """Initialisiert die Session-State-Variablen"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user" not in st.session_state:
        st.session_state.user = None

    if "role" not in st.session_state:
        st.session_state.role = None

    if "current_case" not in st.session_state:
        st.session_state.current_case = None


def login_as_demo(role: str):
    """Meldet einen Demo-Benutzer an"""
    demo_users = {
        "admin": {
            "user": {
                "email": "admin@rhm-kanzlei.de",
                "vorname": "Anna",
                "nachname": "Administrator",
                "titel": "",
            },
            "role": "admin",
            "case": None,
        },
        "anwalt": {
            "user": {
                "email": "ra.mueller@rhm-kanzlei.de",
                "vorname": "Dr. Thomas",
                "nachname": "Mueller",
                "titel": "Rechtsanwalt",
                "fachanwalt": "Familienrecht",
            },
            "role": "anwalt",
            "case": None,
        },
        "mitarbeiter": {
            "user": {
                "email": "sekretariat@rhm-kanzlei.de",
                "vorname": "Sandra",
                "nachname": "Schmidt",
                "titel": "",
            },
            "role": "mitarbeiter",
            "case": None,
        },
        "mandant": {
            "user": {
                "vorname": "Max",
                "nachname": "Mustermann",
            },
            "role": "mandant",
            "case": {
                "case_number": "2026/0001",
                "case_type": "scheidung",
                "lawyer": "Dr. Thomas Mueller",
            },
        },
    }

    if role in demo_users:
        demo = demo_users[role]
        st.session_state.authenticated = True
        st.session_state.user = demo["user"]
        st.session_state.role = demo["role"]
        st.session_state.current_case = demo["case"]
        st.session_state.is_demo = True
        st.rerun()


def show_login_page():
    """Zeigt die Login-Seite"""
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
        }
        .demo-button {
            margin: 0.25rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## FamilyKom")
        st.markdown("### Familienrechts-Applikation")
        st.markdown("---")

        # Demo-Bereich
        st.markdown("#### Demo-Zugang")
        st.markdown("Testen Sie die Anwendung mit einem Demo-Account:")

        demo_col1, demo_col2 = st.columns(2)

        with demo_col1:
            if st.button("Als Anwalt", use_container_width=True, type="primary"):
                login_as_demo("anwalt")

            if st.button("Als Mitarbeiter", use_container_width=True):
                login_as_demo("mitarbeiter")

        with demo_col2:
            if st.button("Als Mandant", use_container_width=True):
                login_as_demo("mandant")

            if st.button("Als Administrator", use_container_width=True):
                login_as_demo("admin")

        st.markdown("---")

        # Reguläre Anmeldung
        st.markdown("#### Anmeldung")

        # Anmeldeart wählen
        login_type = st.radio(
            "Anmeldung als:",
            ["Anwalt", "Mitarbeiter", "Mandant (mit Zugangscode)"],
            horizontal=True
        )

        st.markdown("")

        if login_type in ["Anwalt", "Mitarbeiter"]:
            with st.form("login_form"):
                email = st.text_input("E-Mail-Adresse")
                password = st.text_input("Passwort", type="password")
                submit = st.form_submit_button("Anmelden", use_container_width=True)

                if submit:
                    if email and password:
                        # TODO: Echte Authentifizierung über Supabase
                        # Temporäre Demo-Logins
                        valid_logins = {
                            # Anwälte
                            ("ra.mueller@rhm-kanzlei.de", "anwalt123"): {
                                "role": "anwalt",
                                "user": {
                                    "email": "ra.mueller@rhm-kanzlei.de",
                                    "vorname": "Dr. Thomas",
                                    "nachname": "Mueller",
                                    "titel": "Rechtsanwalt",
                                }
                            },
                            ("ra.radtke@rhm-kanzlei.de", "anwalt123"): {
                                "role": "anwalt",
                                "user": {
                                    "email": "ra.radtke@rhm-kanzlei.de",
                                    "vorname": "Michael",
                                    "nachname": "Radtke",
                                    "titel": "Rechtsanwalt",
                                }
                            },
                            ("ra.heigener@rhm-kanzlei.de", "anwalt123"): {
                                "role": "anwalt",
                                "user": {
                                    "email": "ra.heigener@rhm-kanzlei.de",
                                    "vorname": "Sabine",
                                    "nachname": "Heigener",
                                    "titel": "Rechtsanwaeltin",
                                }
                            },
                            ("ra.meier@rhm-kanzlei.de", "anwalt123"): {
                                "role": "anwalt",
                                "user": {
                                    "email": "ra.meier@rhm-kanzlei.de",
                                    "vorname": "Klaus",
                                    "nachname": "Meier",
                                    "titel": "Rechtsanwalt",
                                }
                            },
                            # Mitarbeiter
                            ("sekretariat@rhm-kanzlei.de", "mitarbeiter123"): {
                                "role": "mitarbeiter",
                                "user": {
                                    "email": "sekretariat@rhm-kanzlei.de",
                                    "vorname": "Sandra",
                                    "nachname": "Schmidt",
                                }
                            },
                            ("buchhaltung@rhm-kanzlei.de", "mitarbeiter123"): {
                                "role": "mitarbeiter",
                                "user": {
                                    "email": "buchhaltung@rhm-kanzlei.de",
                                    "vorname": "Petra",
                                    "nachname": "Wagner",
                                }
                            },
                            # Admin
                            ("admin@rhm-kanzlei.de", "admin123"): {
                                "role": "admin",
                                "user": {
                                    "email": "admin@rhm-kanzlei.de",
                                    "vorname": "Anna",
                                    "nachname": "Administrator",
                                }
                            },
                        }

                        login_key = (email.lower(), password)
                        if login_key in valid_logins:
                            login_data = valid_logins[login_key]
                            expected_role = "anwalt" if login_type == "Anwalt" else "mitarbeiter"

                            # Prüfe ob Rolle passt (Admin kann sich überall anmelden)
                            if login_data["role"] == expected_role or login_data["role"] == "admin":
                                st.session_state.authenticated = True
                                st.session_state.user = login_data["user"]
                                st.session_state.role = login_data["role"]
                                st.session_state.is_demo = False
                                st.rerun()
                            else:
                                st.error(f"Dieses Konto ist kein {login_type}-Konto")
                        else:
                            st.error("Ungueltige Anmeldedaten")
                    else:
                        st.warning("Bitte E-Mail und Passwort eingeben")

        else:  # Mandanten-Login
            with st.form("mandant_login_form"):
                access_code = st.text_input(
                    "Zugangscode",
                    help="Den Zugangscode haben Sie von Ihrer Kanzlei erhalten"
                )
                submit = st.form_submit_button("Zugang oeffnen", use_container_width=True)

                if submit:
                    if access_code:
                        # TODO: Code-Validierung über Supabase
                        # Temporäre Demo-Codes
                        valid_codes = {
                            "MUSTERMANN2026": {
                                "user": {
                                    "vorname": "Max",
                                    "nachname": "Mustermann",
                                },
                                "case": {
                                    "case_number": "2026/0001",
                                    "case_type": "scheidung",
                                    "lawyer": "Dr. Thomas Mueller",
                                }
                            },
                            "SCHMIDT2026": {
                                "user": {
                                    "vorname": "Lisa",
                                    "nachname": "Schmidt",
                                },
                                "case": {
                                    "case_number": "2026/0015",
                                    "case_type": "kindesunterhalt",
                                    "lawyer": "Sabine Heigener",
                                }
                            },
                            "DEMO123456": {  # Alter Demo-Code bleibt aktiv
                                "user": {
                                    "vorname": "Demo",
                                    "nachname": "Mandant",
                                },
                                "case": {
                                    "case_number": "2026/DEMO",
                                    "case_type": "scheidung",
                                    "lawyer": "Dr. Thomas Mueller",
                                }
                            },
                        }

                        code_upper = access_code.upper().strip()
                        if code_upper in valid_codes:
                            data = valid_codes[code_upper]
                            st.session_state.authenticated = True
                            st.session_state.user = data["user"]
                            st.session_state.role = "mandant"
                            st.session_state.current_case = data["case"]
                            st.session_state.is_demo = False
                            st.rerun()
                        else:
                            st.error("Ungueltiger Zugangscode")
                    else:
                        st.warning("Bitte Zugangscode eingeben")

        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #888; font-size: 0.8rem;">
            RHM - Radtke, Heigener und Meier<br>
            Kanzlei fuer Familienrecht, Rendsburg<br>
            </div>
            """,
            unsafe_allow_html=True
        )


def show_sidebar():
    """Zeigt die Sidebar je nach Benutzerrolle"""
    with st.sidebar:
        st.markdown(f"### FamilyKom")

        user = st.session_state.user
        role = st.session_state.role
        is_demo = st.session_state.get("is_demo", False)

        # Demo-Badge anzeigen
        if is_demo:
            st.warning("Demo-Modus")

        # Benutzerinfo mit Titel/Rolle
        titel = user.get("titel", "")
        if titel:
            st.markdown(f"**{titel}**")
            st.markdown(f"**{user.get('vorname')} {user.get('nachname')}**")
        else:
            st.markdown(f"**{user.get('vorname')} {user.get('nachname')}**")

        # Rollen-Anzeige
        role_labels = {
            "admin": "Administrator",
            "anwalt": "Rechtsanwalt/in",
            "mitarbeiter": "Kanzleimitarbeiter/in",
            "mandant": "Mandant/in",
        }
        st.markdown(f"*{role_labels.get(role, role.title())}*")

        st.markdown("---")

        if role == "admin":
            show_admin_menu()
        elif role == "anwalt":
            show_anwalt_menu()
        elif role == "mitarbeiter":
            show_mitarbeiter_menu()
        elif role == "mandant":
            show_mandant_menu()

        st.markdown("---")

        if st.button("Abmelden", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def show_admin_menu():
    """Admin-Menü in der Sidebar"""
    st.markdown("#### Administration")

    menu = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Benutzerverwaltung",
            "Tabellen-Updates",
            "Systemüberwachung",
            "Einstellungen",
        ],
        label_visibility="collapsed"
    )

    st.session_state.current_page = menu


def show_anwalt_menu():
    """Anwalts-Menü in der Sidebar"""
    st.markdown("#### Aktenmanagement")

    menu = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Akten",
            "Neue Akte",
            "---",
            "Kindesunterhalt",
            "Ehegattenunterhalt",
            "Zugewinnausgleich",
            "RVG-Gebuehren",
            "---",
            "Schriftsaetze",
            "Dokumente",
        ],
        label_visibility="collapsed"
    )

    # Entferne Trennzeichen aus der Auswahl
    if menu == "---":
        menu = "Dashboard"

    st.session_state.current_page = menu


def show_mitarbeiter_menu():
    """Mitarbeiter-Menü in der Sidebar (eingeschränkte Funktionen)"""
    st.markdown("#### Kanzlei")

    menu = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Akten",
            "---",
            "Kindesunterhalt",
            "Ehegattenunterhalt",
            "Zugewinnausgleich",
            "RVG-Gebuehren",
            "---",
            "Dokumente",
            "Fristen",
        ],
        label_visibility="collapsed"
    )

    # Entferne Trennzeichen aus der Auswahl
    if menu == "---":
        menu = "Dashboard"

    st.session_state.current_page = menu


def show_mandant_menu():
    """Mandanten-Menü in der Sidebar"""
    st.markdown("#### Meine Akte")

    case = st.session_state.current_case
    if case:
        st.info(f"Az.: {case.get('case_number')}")

    menu = st.radio(
        "Navigation",
        [
            "Übersicht",
            "Dokumente hochladen",
            "Meine Dokumente",
            "Berechnungen",
            "Nachrichten",
        ],
        label_visibility="collapsed"
    )

    st.session_state.current_page = menu


def show_main_content():
    """Zeigt den Hauptinhalt basierend auf der aktuellen Seite"""
    page = st.session_state.get("current_page", "Dashboard")
    role = st.session_state.role

    # Admin-Seiten
    if role == "admin":
        if page == "Dashboard":
            show_admin_dashboard()
        elif page == "Benutzerverwaltung":
            show_user_management()
        elif page == "Tabellen-Updates":
            show_table_updates()
        elif page == "Systemüberwachung":
            show_system_monitoring()
        elif page == "Einstellungen":
            show_settings()

    # Anwalts-Seiten
    elif role == "anwalt":
        if page == "Dashboard":
            show_lawyer_dashboard()
        elif page == "Akten":
            show_cases_list()
        elif page == "Neue Akte":
            show_new_case()
        elif page == "Kindesunterhalt":
            show_kindesunterhalt_calculator()
        elif page == "Ehegattenunterhalt":
            show_ehegattenunterhalt_calculator()
        elif page == "Zugewinnausgleich":
            show_zugewinn_calculator()
        elif page == "RVG-Gebuehren":
            show_rvg_calculator()
        elif page == "Schriftsaetze":
            show_documents_templates()
        elif page == "Dokumente":
            show_documents_management()

    # Mitarbeiter-Seiten
    elif role == "mitarbeiter":
        if page == "Dashboard":
            show_mitarbeiter_dashboard()
        elif page == "Akten":
            show_cases_list()
        elif page == "Kindesunterhalt":
            show_kindesunterhalt_calculator()
        elif page == "Ehegattenunterhalt":
            show_ehegattenunterhalt_calculator()
        elif page == "Zugewinnausgleich":
            show_zugewinn_calculator()
        elif page == "RVG-Gebuehren":
            show_rvg_calculator()
        elif page == "Dokumente":
            show_documents_management()
        elif page == "Fristen":
            show_fristen_management()

    # Mandanten-Seiten
    elif role == "mandant":
        if page == "Übersicht":
            show_client_overview()
        elif page == "Dokumente hochladen":
            show_document_upload()
        elif page == "Meine Dokumente":
            show_client_documents()
        elif page == "Berechnungen":
            show_client_calculations()
        elif page == "Nachrichten":
            show_client_messages()


# =============================================================================
# Admin-Seiten (Platzhalter)
# =============================================================================

def show_admin_dashboard():
    st.header("Administrator-Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Aktive Benutzer", "12")
    with col2:
        st.metric("Offene Akten", "47")
    with col3:
        st.metric("Dokumente heute", "23")
    with col4:
        st.metric("Speicher", "2.4 GB")


def show_user_management():
    st.header("Benutzerverwaltung")
    st.info("Hier können Benutzer verwaltet werden.")


def show_table_updates():
    st.header("Tabellen-Updates")
    st.info("Aktualisierung der Düsseldorfer Tabelle und OLG-Leitlinien.")


def show_system_monitoring():
    st.header("Systemüberwachung")
    st.info("System-Status und Logs.")


def show_settings():
    st.header("Einstellungen")
    st.info("Systemeinstellungen.")


# =============================================================================
# Anwalts-Seiten (Platzhalter)
# =============================================================================

def show_lawyer_dashboard():
    st.header("Dashboard")

    user = st.session_state.user
    st.markdown(f"Willkommen, **{user.get('titel', '')} {user.get('vorname')} {user.get('nachname')}**")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Aktive Akten", "15")
    with col2:
        st.metric("Offene Anforderungen", "7")
    with col3:
        st.metric("Termine diese Woche", "4")
    with col4:
        st.metric("Fristen (7 Tage)", "3")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Naechste Termine")
        st.info("15.01.2026 10:00 - AG Rendsburg, Az. 2026/0001")
        st.info("17.01.2026 14:30 - Mandantentermin Mustermann")

    with col2:
        st.subheader("Letzte Aktivitaeten")
        st.success("Dokument hochgeladen: Einkommensnachweis (Az. 2026/0015)")
        st.success("Berechnung erstellt: Kindesunterhalt (Az. 2026/0008)")


def show_mitarbeiter_dashboard():
    st.header("Dashboard")

    user = st.session_state.user
    st.markdown(f"Willkommen, **{user.get('vorname')} {user.get('nachname')}**")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Offene Akten", "47")
    with col2:
        st.metric("Dokumente heute", "12")
    with col3:
        st.metric("Offene Fristen", "8")
    with col4:
        st.metric("Mandantenanfragen", "3")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dringende Fristen")
        st.warning("14.01.2026 - Schriftsatzfrist Az. 2026/0003")
        st.warning("16.01.2026 - Stellungnahmefrist Az. 2026/0012")
        st.info("20.01.2026 - Wiedervorlage Az. 2026/0001")

    with col2:
        st.subheader("Offene Dokumentenanforderungen")
        st.info("Az. 2026/0015 - Einkommensnachweis ausstehend")
        st.info("Az. 2026/0008 - Geburtsurkunde ausstehend")


def show_fristen_management():
    st.header("Fristenverwaltung")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Anstehende Fristen")

    with col2:
        filter_option = st.selectbox(
            "Zeitraum",
            ["Naechste 7 Tage", "Naechste 14 Tage", "Naechste 30 Tage", "Alle"]
        )

    # Demo-Fristen
    fristen = [
        {"datum": "14.01.2026", "typ": "Schriftsatzfrist", "akte": "2026/0003", "anwalt": "Dr. Mueller", "status": "offen"},
        {"datum": "16.01.2026", "typ": "Stellungnahmefrist", "akte": "2026/0012", "anwalt": "Heigener", "status": "offen"},
        {"datum": "20.01.2026", "typ": "Wiedervorlage", "akte": "2026/0001", "anwalt": "Dr. Mueller", "status": "offen"},
        {"datum": "25.01.2026", "typ": "Berufungsfrist", "akte": "2025/0089", "anwalt": "Radtke", "status": "offen"},
        {"datum": "31.01.2026", "typ": "Verjaehrung", "akte": "2024/0156", "anwalt": "Meier", "status": "geprueft"},
    ]

    for frist in fristen:
        col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
        with col1:
            st.write(frist["datum"])
        with col2:
            st.write(f"**{frist['typ']}**")
        with col3:
            st.write(f"Az. {frist['akte']}")
        with col4:
            st.write(frist["anwalt"])
        with col5:
            if frist["status"] == "offen":
                st.error("Offen")
            else:
                st.success("Geprueft")
        st.markdown("---")


def show_cases_list():
    st.header("Aktenübersicht")
    st.info("Liste aller Akten mit Such- und Filterfunktion.")


def show_new_case():
    st.header("Neue Akte anlegen")
    st.info("Formular zur Anlage einer neuen Akte.")


def show_kindesunterhalt_calculator():
    """Kindesunterhalt-Rechner"""
    from src.pages.anwalt.kindesunterhalt import render_kindesunterhalt_page
    render_kindesunterhalt_page()


def show_ehegattenunterhalt_calculator():
    """Ehegattenunterhalt-Rechner"""
    from src.pages.anwalt.ehegattenunterhalt import render_ehegattenunterhalt_page
    render_ehegattenunterhalt_page()


def show_zugewinn_calculator():
    """Zugewinnausgleich-Rechner"""
    from src.pages.anwalt.zugewinn import render_zugewinn_page
    render_zugewinn_page()


def show_rvg_calculator():
    """RVG-Gebührenrechner"""
    from src.pages.anwalt.rvg import render_rvg_page
    render_rvg_page()


def show_documents_templates():
    st.header("Schriftsätze")
    st.info("Schriftsatzvorlagen und -erstellung.")


def show_documents_management():
    st.header("Dokumentenverwaltung")
    st.info("Dokumentenübersicht und -verwaltung.")


# =============================================================================
# Mandanten-Seiten (Platzhalter)
# =============================================================================

def show_client_overview():
    st.header("Willkommen")
    user = st.session_state.user
    st.markdown(f"Guten Tag, **{user.get('vorname')} {user.get('nachname')}**")

    case = st.session_state.current_case
    if case:
        st.info(f"Ihre Akte: {case.get('case_number')} ({case.get('case_type', '').title()})")

    st.markdown("---")
    st.subheader("Offene Anforderungen")
    st.warning("Bitte laden Sie die folgenden Dokumente hoch...")


def show_document_upload():
    st.header("Dokumente hochladen")
    st.info("Laden Sie hier Ihre Dokumente hoch.")


def show_client_documents():
    st.header("Meine Dokumente")
    st.info("Übersicht Ihrer hochgeladenen Dokumente.")


def show_client_calculations():
    st.header("Berechnungen")
    st.info("Freigegebene Berechnungen Ihres Anwalts.")


def show_client_messages():
    st.header("Nachrichten")
    st.info("Kommunikation mit Ihrer Kanzlei.")


# =============================================================================
# Hauptprogramm
# =============================================================================

def main():
    """Hauptfunktion der Anwendung"""
    init_session_state()

    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_sidebar()
        show_main_content()


if __name__ == "__main__":
    main()
