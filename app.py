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


def show_login_page():
    """Zeigt die Login-Seite"""
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
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

        # Anmeldeart wählen
        login_type = st.radio(
            "Anmeldung als:",
            ["Kanzlei-Mitarbeiter", "Mandant (mit Zugangscode)"],
            horizontal=True
        )

        st.markdown("")

        if login_type == "Kanzlei-Mitarbeiter":
            with st.form("login_form"):
                email = st.text_input("E-Mail-Adresse")
                password = st.text_input("Passwort", type="password")
                submit = st.form_submit_button("Anmelden", use_container_width=True)

                if submit:
                    if email and password:
                        # TODO: Echte Authentifizierung über Supabase
                        # Demo-Login für Entwicklung
                        if email == "demo@rhm-kanzlei.de" and password == "demo":
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                "email": email,
                                "vorname": "Demo",
                                "nachname": "Anwalt",
                            }
                            st.session_state.role = "anwalt"
                            st.rerun()
                        elif email == "admin@rhm-kanzlei.de" and password == "admin":
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                "email": email,
                                "vorname": "Admin",
                                "nachname": "User",
                            }
                            st.session_state.role = "admin"
                            st.rerun()
                        else:
                            st.error("Ungültige Anmeldedaten")
                    else:
                        st.warning("Bitte E-Mail und Passwort eingeben")

        else:  # Mandanten-Login
            with st.form("mandant_login_form"):
                access_code = st.text_input(
                    "Zugangscode",
                    help="Den Zugangscode haben Sie von Ihrer Kanzlei erhalten"
                )
                submit = st.form_submit_button("Zugang öffnen", use_container_width=True)

                if submit:
                    if access_code:
                        # TODO: Code-Validierung über Supabase
                        # Demo-Login
                        if access_code == "DEMO123456":
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                "vorname": "Max",
                                "nachname": "Mustermann",
                            }
                            st.session_state.role = "mandant"
                            st.session_state.current_case = {
                                "case_number": "2025/0001",
                                "case_type": "scheidung",
                            }
                            st.rerun()
                        else:
                            st.error("Ungültiger Zugangscode")
                    else:
                        st.warning("Bitte Zugangscode eingeben")

        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #888; font-size: 0.8rem;">
            RHM - Radtke, Heigener und Meier<br>
            Kanzlei für Familienrecht, Rendsburg<br>
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

        st.markdown(f"**{user.get('vorname')} {user.get('nachname')}**")
        st.markdown(f"*{role.title()}*")

        st.markdown("---")

        if role == "admin":
            show_admin_menu()
        elif role == "anwalt":
            show_anwalt_menu()
        elif role == "mitarbeiter":
            show_anwalt_menu()  # Gleiche Optionen wie Anwalt
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
            "RVG-Gebühren",
            "---",
            "Schriftsätze",
            "Dokumente",
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
    elif role in ["anwalt", "mitarbeiter"]:
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
        elif page == "RVG-Gebühren":
            show_rvg_calculator()
        elif page == "Schriftsätze":
            show_documents_templates()
        elif page == "Dokumente":
            show_documents_management()

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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Aktive Akten", "15")
    with col2:
        st.metric("Offene Anforderungen", "7")
    with col3:
        st.metric("Termine diese Woche", "4")

    st.markdown("---")
    st.subheader("Letzte Aktivitäten")
    st.info("Hier werden die letzten Aktivitäten angezeigt.")


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
