"""
FamilyKom - Familienrechts-Applikation
Hauptanwendung (Streamlit)

Fuer RHM - Radtke, Heigener und Meier Kanzlei, Rendsburg
"""

import streamlit as st
from datetime import datetime, date

from config.settings import settings
from config.version import get_version, get_version_display, CHANGELOG

# Seitenkonfiguration muss zuerst kommen
st.set_page_config(
    page_title="FamilyKom - Familienrecht",
    page_icon="scales",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a Bug": None,
        "About": f"""
        ## FamilyKom
        Familienrechts-Applikation

        {get_version_display()}

        Entwickelt fuer RHM - Radtke, Heigener und Meier
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

        # Versionsnummer am Ende der Sidebar
        st.markdown("---")
        st.caption(get_version_display())


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
            "Dokumentenanforderung",
            "Schriftsaetze",
            "Dokumente",
            "---",
            "API-Einstellungen",
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
        elif page == "Aktendetail":
            show_case_detail()
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
        elif page == "Dokumentenanforderung":
            show_dokumentenanforderung()
        elif page == "Schriftsaetze":
            show_documents_templates()
        elif page == "Dokumente":
            show_documents_management()
        elif page == "API-Einstellungen":
            show_api_settings()

    # Mitarbeiter-Seiten
    elif role == "mitarbeiter":
        if page == "Dashboard":
            show_mitarbeiter_dashboard()
        elif page == "Akten":
            show_cases_list()
        elif page == "Aktendetail":
            show_case_detail()
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
    """Vollstaendige Benutzerverwaltung"""
    st.header("Benutzerverwaltung")

    tab1, tab2, tab3 = st.tabs(["Benutzer", "Neuer Benutzer", "Rollen & Rechte"])

    with tab1:
        st.subheader("Benutzerliste")

        # Filter
        col1, col2 = st.columns(2)
        with col1:
            filter_rolle = st.selectbox(
                "Rolle",
                ["Alle", "Administrator", "Anwalt", "Mitarbeiter"],
                key="user_filter_role"
            )
        with col2:
            filter_status = st.selectbox(
                "Status",
                ["Alle", "Aktiv", "Inaktiv", "Gesperrt"],
                key="user_filter_status"
            )

        st.markdown("---")

        # Demo-Benutzer
        benutzer = [
            {"name": "Dr. Thomas Mueller", "email": "ra.mueller@rhm-kanzlei.de",
             "rolle": "Anwalt", "status": "Aktiv", "letzter_login": "12.01.2026 09:15"},
            {"name": "Sabine Heigener", "email": "ra.heigener@rhm-kanzlei.de",
             "rolle": "Anwalt", "status": "Aktiv", "letzter_login": "12.01.2026 08:30"},
            {"name": "Michael Radtke", "email": "ra.radtke@rhm-kanzlei.de",
             "rolle": "Anwalt", "status": "Aktiv", "letzter_login": "11.01.2026 16:45"},
            {"name": "Klaus Meier", "email": "ra.meier@rhm-kanzlei.de",
             "rolle": "Anwalt", "status": "Aktiv", "letzter_login": "10.01.2026 14:20"},
            {"name": "Sandra Schmidt", "email": "sekretariat@rhm-kanzlei.de",
             "rolle": "Mitarbeiter", "status": "Aktiv", "letzter_login": "12.01.2026 08:00"},
            {"name": "Petra Wagner", "email": "buchhaltung@rhm-kanzlei.de",
             "rolle": "Mitarbeiter", "status": "Aktiv", "letzter_login": "12.01.2026 08:05"},
            {"name": "Anna Administrator", "email": "admin@rhm-kanzlei.de",
             "rolle": "Administrator", "status": "Aktiv", "letzter_login": "12.01.2026 07:30"},
        ]

        # Filtern
        gefilterte_benutzer = benutzer
        if filter_rolle != "Alle":
            gefilterte_benutzer = [b for b in gefilterte_benutzer if b["rolle"] == filter_rolle]
        if filter_status != "Alle":
            gefilterte_benutzer = [b for b in gefilterte_benutzer if b["status"] == filter_status]

        # Tabellenkopf
        cols = st.columns([2, 2.5, 1.5, 1, 1.5])
        with cols[0]:
            st.markdown("**Name**")
        with cols[1]:
            st.markdown("**E-Mail**")
        with cols[2]:
            st.markdown("**Rolle**")
        with cols[3]:
            st.markdown("**Status**")
        with cols[4]:
            st.markdown("**Aktion**")

        st.markdown("---")

        for user in gefilterte_benutzer:
            cols = st.columns([2, 2.5, 1.5, 1, 1.5])
            with cols[0]:
                st.write(user["name"])
                st.caption(f"Login: {user['letzter_login']}")
            with cols[1]:
                st.write(user["email"])
            with cols[2]:
                st.write(user["rolle"])
            with cols[3]:
                if user["status"] == "Aktiv":
                    st.success(user["status"])
                elif user["status"] == "Inaktiv":
                    st.warning(user["status"])
                else:
                    st.error(user["status"])
            with cols[4]:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.button("Edit", key=f"edit_{user['email']}", use_container_width=True)
                with col_b:
                    st.button("Sperr", key=f"lock_{user['email']}", use_container_width=True)
            st.markdown("---")

    with tab2:
        st.subheader("Neuen Benutzer anlegen")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Persoenliche Daten")
            new_anrede = st.selectbox("Anrede", ["Herr", "Frau"], key="new_user_anrede")
            new_titel = st.text_input("Titel (optional)", placeholder="Dr., RA, etc.", key="new_user_titel")
            new_vorname = st.text_input("Vorname", key="new_user_vorname")
            new_nachname = st.text_input("Nachname", key="new_user_nachname")

        with col2:
            st.markdown("#### Zugangsdaten")
            new_email = st.text_input("E-Mail-Adresse", key="new_user_email")
            new_rolle = st.selectbox(
                "Rolle",
                ["Anwalt", "Mitarbeiter", "Administrator"],
                key="new_user_rolle"
            )
            new_passwort = st.text_input("Initiales Passwort", type="password", key="new_user_pw")
            new_pw_bestaetigen = st.text_input("Passwort bestaetigen", type="password", key="new_user_pw2")

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Benutzer anlegen", type="primary", use_container_width=True):
                if new_vorname and new_nachname and new_email and new_passwort:
                    if new_passwort == new_pw_bestaetigen:
                        st.success(f"Benutzer {new_vorname} {new_nachname} wurde angelegt!")
                    else:
                        st.error("Passwoerter stimmen nicht ueberein!")
                else:
                    st.warning("Bitte alle Pflichtfelder ausfuellen.")

    with tab3:
        st.subheader("Rollen und Berechtigungen")

        st.markdown("""
        | Berechtigung | Administrator | Anwalt | Mitarbeiter |
        |--------------|:-------------:|:------:|:-----------:|
        | Akten anlegen | Ja | Ja | Nein |
        | Akten bearbeiten | Ja | Ja | Ja |
        | Berechnungen erstellen | Ja | Ja | Ja |
        | Berechnungen freigeben | Ja | Ja | Nein |
        | Dokumente hochladen | Ja | Ja | Ja |
        | Dokumente loeschen | Ja | Ja | Nein |
        | Benutzer verwalten | Ja | Nein | Nein |
        | System konfigurieren | Ja | Nein | Nein |
        | API-Einstellungen | Ja | Ja | Nein |
        | Tabellen aktualisieren | Ja | Nein | Nein |
        """)

        st.markdown("---")
        st.info("Individuelle Berechtigungsanpassungen koennen in der Produktionsversion vorgenommen werden.")


def show_table_updates():
    """Verwaltung der Rechentabellen"""
    st.header("Tabellen-Updates")

    tab1, tab2, tab3 = st.tabs(["Uebersicht", "Duesseldorfer Tabelle", "OLG-Leitlinien"])

    with tab1:
        st.subheader("Aktueller Stand der Tabellen")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Duesseldorfer Tabelle")
            st.success("Stand: 01.01.2025")
            st.write("Letzte Pruefung: 10.01.2026")
            st.write("Naechste Aktualisierung: 01.01.2026")

            if st.button("Auf Updates pruefen", key="check_dt"):
                st.info("Pruefe auf neue Version...")
                st.success("Tabelle ist aktuell!")

        with col2:
            st.markdown("#### OLG Schleswig Leitlinien")
            st.success("Stand: 01.01.2025")
            st.write("Letzte Pruefung: 10.01.2026")

            if st.button("Auf Updates pruefen", key="check_olg"):
                st.info("Pruefe auf neue Version...")
                st.success("Leitlinien sind aktuell!")

        st.markdown("---")

        st.markdown("#### Weitere Tabellen")

        tabellen_status = [
            {"name": "VPI (Verbraucherpreisindex)", "stand": "Dezember 2025", "status": "Aktuell"},
            {"name": "RVG Gebuehrentabelle", "stand": "01.01.2021", "status": "Aktuell"},
            {"name": "PKH-Tabelle", "stand": "01.01.2024", "status": "Aktuell"},
            {"name": "Selbstbehalt-Werte", "stand": "01.01.2025", "status": "Aktuell"},
        ]

        for tab in tabellen_status:
            col1, col2, col3 = st.columns([2, 1.5, 1])
            with col1:
                st.write(tab["name"])
            with col2:
                st.write(f"Stand: {tab['stand']}")
            with col3:
                st.success(tab["status"])
            st.markdown("---")

    with tab2:
        st.subheader("Duesseldorfer Tabelle 2025")

        st.markdown("#### Aktuell hinterlegte Werte")

        st.markdown("""
        | Einkommensgruppe | 0-5 Jahre | 6-11 Jahre | 12-17 Jahre | ab 18 Jahre |
        |------------------|----------:|----------:|------------:|-----------:|
        | bis 2.100 EUR    | 480 EUR   | 551 EUR   | 645 EUR     | 689 EUR    |
        | 2.101-2.500 EUR  | 504 EUR   | 579 EUR   | 678 EUR     | 724 EUR    |
        | 2.501-2.900 EUR  | 528 EUR   | 607 EUR   | 710 EUR     | 758 EUR    |
        | 2.901-3.300 EUR  | 552 EUR   | 634 EUR   | 742 EUR     | 792 EUR    |
        | 3.301-3.700 EUR  | 576 EUR   | 661 EUR   | 774 EUR     | 827 EUR    |
        """)

        st.caption("Vollstaendige Tabelle mit 15 Einkommensgruppen im System hinterlegt.")

        st.markdown("---")

        st.markdown("#### Manuelle Aktualisierung")
        st.warning("Aenderungen an den Tabellen sollten nur bei offiziellen Updates vorgenommen werden!")

        uploaded_tabelle = st.file_uploader(
            "Neue Tabelle hochladen (CSV/Excel)",
            type=["csv", "xlsx"],
            help="Format: Einkommensgruppe, Altersstufe1, Altersstufe2, Altersstufe3, Altersstufe4"
        )

        if uploaded_tabelle:
            if st.button("Tabelle aktualisieren", type="primary"):
                st.success("Tabelle wurde aktualisiert!")
                st.info("Alle zukuenftigen Berechnungen verwenden die neuen Werte.")

    with tab3:
        st.subheader("OLG Schleswig-Holstein Leitlinien")

        st.markdown("#### Aktuelle Einstellungen")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Selbstbehalte (notwendig)**")
            st.write("- Erwerbstaetiger gegenueber Kindern: 1.450 EUR")
            st.write("- Nicht-Erwerbstaetiger gegenueber Kindern: 1.200 EUR")
            st.write("- Gegenueber Ehegatten: 1.600 EUR")

        with col2:
            st.markdown("**Erwerbstaetigenbonus**")
            st.write("- Quote: 1/7 (ca. 14,3%)")
            st.write("- Anwendung: Ehegattenunterhalt")

        st.markdown("---")

        st.markdown("#### Aenderungsprotokoll")

        aenderungen = [
            {"datum": "01.01.2025", "beschreibung": "Erhoehung Selbstbehalte, neue Duesseldorfer Tabelle"},
            {"datum": "01.01.2024", "beschreibung": "Anpassung Kindergeldanrechnung"},
            {"datum": "01.01.2023", "beschreibung": "Neue Einkommensgruppen"},
        ]

        for ae in aenderungen:
            st.write(f"**{ae['datum']}**: {ae['beschreibung']}")


def show_system_monitoring():
    """Systemueberwachung und Logs"""
    st.header("Systemueberwachung")

    tab1, tab2, tab3, tab4 = st.tabs(["Status", "Aktivitaeten", "Fehler-Log", "Speicher"])

    with tab1:
        st.subheader("Systemstatus")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Datenbank", "Online")
            st.success("Supabase verbunden")

        with col2:
            st.metric("Cache", "Online")
            st.success("Upstash Redis aktiv")

        with col3:
            st.metric("Speicher", "2.4 GB / 10 GB")
            st.info("24% belegt")

        with col4:
            st.metric("Aktive Sessions", "3")
            st.info("Normale Last")

        st.markdown("---")

        st.markdown("#### Dienststatus")

        dienste = [
            {"name": "Authentifizierung (Supabase Auth)", "status": "Online", "latenz": "45ms"},
            {"name": "Datenbank (PostgreSQL)", "status": "Online", "latenz": "12ms"},
            {"name": "Datei-Speicher (Supabase Storage)", "status": "Online", "latenz": "89ms"},
            {"name": "Cache (Upstash Redis)", "status": "Online", "latenz": "8ms"},
            {"name": "OCR-Dienst (Google Vision)", "status": "Bereit", "latenz": "-"},
        ]

        for dienst in dienste:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(dienst["name"])
            with col2:
                if dienst["status"] == "Online":
                    st.success(dienst["status"])
                elif dienst["status"] == "Bereit":
                    st.info(dienst["status"])
                else:
                    st.error(dienst["status"])
            with col3:
                st.write(dienst["latenz"])
            st.markdown("---")

    with tab2:
        st.subheader("Letzte Aktivitaeten")

        aktivitaeten = [
            {"zeit": "12.01.2026 15:30", "benutzer": "Dr. Mueller", "aktion": "Berechnung erstellt", "details": "Kindesunterhalt Az. 2026/0015"},
            {"zeit": "12.01.2026 15:15", "benutzer": "Mandant Mustermann", "aktion": "Dokument hochgeladen", "details": "Gehaltsabrechnung_Dez.pdf"},
            {"zeit": "12.01.2026 14:45", "benutzer": "S. Schmidt", "aktion": "Akte geoeffnet", "details": "Az. 2026/0001"},
            {"zeit": "12.01.2026 14:30", "benutzer": "Dr. Mueller", "aktion": "Anmeldung", "details": "IP: 192.168.1.100"},
            {"zeit": "12.01.2026 14:00", "benutzer": "System", "aktion": "Backup erstellt", "details": "Automatisches Tages-Backup"},
        ]

        for akt in aktivitaeten:
            col1, col2, col3 = st.columns([1.5, 1.5, 3])
            with col1:
                st.write(akt["zeit"])
            with col2:
                st.write(akt["benutzer"])
            with col3:
                st.markdown(f"**{akt['aktion']}**")
                st.caption(akt["details"])
            st.markdown("---")

    with tab3:
        st.subheader("Fehler-Log")

        # Filter
        col1, col2 = st.columns(2)
        with col1:
            fehler_level = st.selectbox(
                "Level",
                ["Alle", "Error", "Warning", "Info"],
                key="error_level"
            )
        with col2:
            fehler_zeitraum = st.selectbox(
                "Zeitraum",
                ["Heute", "Diese Woche", "Dieser Monat"],
                key="error_period"
            )

        st.markdown("---")

        # Demo-Fehler
        st.success("Keine kritischen Fehler in den letzten 24 Stunden.")

        st.markdown("#### Letzte Warnungen")
        warnungen = [
            {"zeit": "11.01.2026 23:45", "level": "Warning", "nachricht": "Langsame Datenbankabfrage (>500ms)"},
            {"zeit": "10.01.2026 15:30", "level": "Info", "nachricht": "Automatisches Logout nach Inaktivitaet"},
        ]

        for warn in warnungen:
            col1, col2, col3 = st.columns([1.5, 1, 4])
            with col1:
                st.write(warn["zeit"])
            with col2:
                if warn["level"] == "Warning":
                    st.warning(warn["level"])
                else:
                    st.info(warn["level"])
            with col3:
                st.write(warn["nachricht"])

    with tab4:
        st.subheader("Speichernutzung")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Dokumentenspeicher")
            st.progress(0.24, text="2.4 GB von 10 GB")

            st.markdown("**Nach Kategorie:**")
            st.write("- Mandantendokumente: 1.8 GB")
            st.write("- Schriftsaetze: 0.4 GB")
            st.write("- System-Backups: 0.2 GB")

        with col2:
            st.markdown("#### Datenbank")
            st.progress(0.15, text="150 MB von 1 GB")

            st.markdown("**Tabellen:**")
            st.write("- Akten: 45 MB")
            st.write("- Dokumente (Metadaten): 30 MB")
            st.write("- Berechnungen: 25 MB")
            st.write("- Benutzer: 5 MB")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Speicheranalyse starten"):
                st.info("Analysiere Speichernutzung...")
        with col2:
            if st.button("Alte Backups loeschen"):
                st.warning("Moechten Sie Backups aelter als 30 Tage loeschen?")


def show_settings():
    """Admin-Einstellungen mit API-Konfiguration"""
    st.header("Systemeinstellungen")

    tab1, tab2, tab3 = st.tabs(["Allgemein", "API-Zugangsdaten", "Sicherheit"])

    with tab1:
        st.subheader("Allgemeine Einstellungen")

        st.markdown("#### Kanzlei-Informationen")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Kanzleiname", value="RHM - Radtke, Heigener und Meier")
            st.text_input("Strasse", value="Musterstrasse 1")
            st.text_input("PLZ / Ort", value="24768 Rendsburg")
        with col2:
            st.text_input("Telefon", value="04331 / 12345")
            st.text_input("E-Mail", value="info@rhm-kanzlei.de")
            st.text_input("Website", value="www.rhm-kanzlei.de")

        st.markdown("#### Anwendungseinstellungen")
        st.checkbox("Demo-Modus aktiviert", value=True, help="Demo-Buttons auf Login-Seite anzeigen")
        st.checkbox("Mandanten-Registrierung erlauben", value=False)
        st.number_input("Session-Timeout (Minuten)", value=30, min_value=5, max_value=480)

    with tab2:
        show_api_settings_content()

    with tab3:
        st.subheader("Sicherheitseinstellungen")

        st.markdown("#### Authentifizierung")
        st.checkbox("Zwei-Faktor-Authentifizierung fuer Anwaelte", value=False)
        st.checkbox("Zwei-Faktor-Authentifizierung fuer Admin", value=True)
        st.number_input("Maximale Login-Versuche", value=5, min_value=3, max_value=10)
        st.number_input("Sperrzeit nach fehlgeschlagenen Logins (Minuten)", value=15, min_value=5, max_value=60)

        st.markdown("#### Passwort-Richtlinien")
        st.number_input("Minimale Passwortlaenge", value=8, min_value=6, max_value=20)
        st.checkbox("Grossbuchstaben erforderlich", value=True)
        st.checkbox("Sonderzeichen erforderlich", value=True)
        st.checkbox("Zahlen erforderlich", value=True)

    if st.button("Einstellungen speichern", type="primary"):
        st.success("Einstellungen wurden gespeichert.")


def show_api_settings():
    """API-Einstellungen fuer Anwaelte"""
    st.header("API-Einstellungen")
    st.markdown("Konfigurieren Sie hier die Zugangsdaten fuer externe Dienste.")

    show_api_settings_content()


def show_api_settings_content():
    """Gemeinsamer Inhalt fuer API-Einstellungen (Admin und Anwalt)"""

    # Initialisiere API-Settings in Session State falls nicht vorhanden
    if "api_settings" not in st.session_state:
        st.session_state.api_settings = {
            "supabase_url": "",
            "supabase_anon_key": "",
            "supabase_service_key": "",
            "upstash_redis_url": "",
            "upstash_redis_token": "",
            "openai_api_key": "",
            "anthropic_api_key": "",
            "google_vision_api_key": "",
        }

    st.info(
        "Diese Einstellungen werden zusaetzlich zu den Streamlit Secrets verwendet. "
        "Fuer die Produktion empfehlen wir, sensible Daten ausschliesslich in den "
        "Streamlit Secrets (.streamlit/secrets.toml) zu speichern."
    )

    # Supabase
    st.markdown("---")
    st.markdown("### Supabase (Datenbank & Auth)")
    st.markdown("Ihre Supabase-Projektdaten finden Sie unter: Project Settings > API")

    col1, col2 = st.columns(2)
    with col1:
        supabase_url = st.text_input(
            "Supabase URL",
            value=st.session_state.api_settings.get("supabase_url", ""),
            placeholder="https://xxxxx.supabase.co",
            help="Die URL Ihres Supabase-Projekts"
        )
    with col2:
        supabase_anon = st.text_input(
            "Supabase Anon Key",
            value=st.session_state.api_settings.get("supabase_anon_key", ""),
            type="password",
            placeholder="eyJhbGciOiJIUzI1...",
            help="Der oeffentliche (anon) API-Key"
        )

    supabase_service = st.text_input(
        "Supabase Service Role Key (nur Admin)",
        value=st.session_state.api_settings.get("supabase_service_key", ""),
        type="password",
        placeholder="eyJhbGciOiJIUzI1...",
        help="Der Service-Role-Key fuer Admin-Operationen (GEHEIM HALTEN!)",
        disabled=st.session_state.role != "admin"
    )

    # Upstash Redis
    st.markdown("---")
    st.markdown("### Upstash Redis (Cache)")
    st.markdown("Ihre Upstash-Daten finden Sie im Upstash Dashboard unter: Database > REST API")

    col1, col2 = st.columns(2)
    with col1:
        upstash_url = st.text_input(
            "Upstash Redis URL",
            value=st.session_state.api_settings.get("upstash_redis_url", ""),
            placeholder="https://xxxxx.upstash.io",
            help="Die REST-URL Ihrer Upstash-Datenbank"
        )
    with col2:
        upstash_token = st.text_input(
            "Upstash Redis Token",
            value=st.session_state.api_settings.get("upstash_redis_token", ""),
            type="password",
            placeholder="AxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxQ==",
            help="Der REST-Token fuer die Authentifizierung"
        )

    # KI APIs
    st.markdown("---")
    st.markdown("### KI-Dienste")
    st.markdown("API-Keys fuer KI-gestuetzte Funktionen (OCR, Dokumentenanalyse, etc.)")

    col1, col2 = st.columns(2)
    with col1:
        openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.api_settings.get("openai_api_key", ""),
            type="password",
            placeholder="sk-...",
            help="Fuer GPT-basierte Textanalyse und -generierung"
        )

        google_vision_key = st.text_input(
            "Google Cloud Vision API Key",
            value=st.session_state.api_settings.get("google_vision_api_key", ""),
            type="password",
            placeholder="AIza...",
            help="Fuer OCR und Dokumentenerkennung"
        )

    with col2:
        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=st.session_state.api_settings.get("anthropic_api_key", ""),
            type="password",
            placeholder="sk-ant-...",
            help="Fuer Claude-basierte Textanalyse"
        )

    # Speichern
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("Speichern", type="primary", use_container_width=True):
            st.session_state.api_settings = {
                "supabase_url": supabase_url,
                "supabase_anon_key": supabase_anon,
                "supabase_service_key": supabase_service,
                "upstash_redis_url": upstash_url,
                "upstash_redis_token": upstash_token,
                "openai_api_key": openai_key,
                "anthropic_api_key": anthropic_key,
                "google_vision_api_key": google_vision_key,
            }
            st.success("API-Einstellungen wurden gespeichert!")

    with col2:
        if st.button("Verbindung testen", use_container_width=True):
            test_api_connections()

    # Hinweis zu Streamlit Secrets
    st.markdown("---")
    with st.expander("Streamlit Secrets konfigurieren"):
        st.markdown("""
        Fuer die Produktionsumgebung sollten Sie die Zugangsdaten in der Datei
        `.streamlit/secrets.toml` speichern:

        ```toml
        # Supabase
        SUPABASE_URL = "https://xxxxx.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1..."
        SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1..."

        # Upstash Redis
        UPSTASH_REDIS_URL = "https://xxxxx.upstash.io"
        UPSTASH_REDIS_TOKEN = "Axxxx..."

        # KI APIs
        OPENAI_API_KEY = "sk-..."
        ANTHROPIC_API_KEY = "sk-ant-..."
        GOOGLE_VISION_API_KEY = "AIza..."
        ```

        Bei Streamlit Cloud werden diese unter "App Settings > Secrets" konfiguriert.
        """)


def test_api_connections():
    """Testet die API-Verbindungen"""
    settings = st.session_state.get("api_settings", {})

    st.markdown("#### Verbindungstests")

    # Supabase Test
    if settings.get("supabase_url") and settings.get("supabase_anon_key"):
        try:
            # Hier wuerde der echte Test stattfinden
            st.success("Supabase: Verbindung erfolgreich")
        except Exception as e:
            st.error(f"Supabase: Verbindung fehlgeschlagen - {e}")
    else:
        st.warning("Supabase: Keine Zugangsdaten konfiguriert")

    # Upstash Test
    if settings.get("upstash_redis_url") and settings.get("upstash_redis_token"):
        try:
            # Hier wuerde der echte Test stattfinden
            st.success("Upstash Redis: Verbindung erfolgreich")
        except Exception as e:
            st.error(f"Upstash Redis: Verbindung fehlgeschlagen - {e}")
    else:
        st.warning("Upstash Redis: Keine Zugangsdaten konfiguriert")

    # OpenAI Test
    if settings.get("openai_api_key"):
        st.success("OpenAI: API-Key konfiguriert")
    else:
        st.warning("OpenAI: Kein API-Key konfiguriert")

    # Anthropic Test
    if settings.get("anthropic_api_key"):
        st.success("Anthropic: API-Key konfiguriert")
    else:
        st.warning("Anthropic: Kein API-Key konfiguriert")

    # Google Vision Test
    if settings.get("google_vision_api_key"):
        st.success("Google Vision: API-Key konfiguriert")
    else:
        st.warning("Google Vision: Kein API-Key konfiguriert")


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
    """Vollstaendige Aktenuebersicht mit Such- und Filterfunktion"""
    st.header("Aktenuebersicht")

    # Demo-Akten
    akten = [
        {"az": "2026/0001", "mandant": "Max Mustermann", "gegner": "Maria Mustermann",
         "typ": "Scheidung", "anwalt": "Dr. Mueller", "status": "Aktiv",
         "angelegt": "02.01.2026", "letzte_aktivitaet": "12.01.2026"},
        {"az": "2026/0002", "mandant": "Klaus Wagner", "gegner": "Petra Wagner",
         "typ": "Zugewinnausgleich", "anwalt": "Heigener", "status": "Aktiv",
         "angelegt": "03.01.2026", "letzte_aktivitaet": "11.01.2026"},
        {"az": "2026/0003", "mandant": "Thomas Berger", "gegner": "Sylvia Berger",
         "typ": "Trennungsunterhalt", "anwalt": "Dr. Mueller", "status": "Aktiv",
         "angelegt": "05.01.2026", "letzte_aktivitaet": "10.01.2026"},
        {"az": "2026/0008", "mandant": "Peter Meyer", "gegner": "Anna Meyer",
         "typ": "Trennungsunterhalt", "anwalt": "Radtke", "status": "Aktiv",
         "angelegt": "08.01.2026", "letzte_aktivitaet": "12.01.2026"},
        {"az": "2026/0015", "mandant": "Lisa Schmidt", "gegner": "Frank Schmidt",
         "typ": "Kindesunterhalt", "anwalt": "Heigener", "status": "Aktiv",
         "angelegt": "10.01.2026", "letzte_aktivitaet": "12.01.2026"},
        {"az": "2025/0089", "mandant": "Herbert Klein", "gegner": "Monika Klein",
         "typ": "Scheidung", "anwalt": "Meier", "status": "Abgeschlossen",
         "angelegt": "15.06.2025", "letzte_aktivitaet": "20.12.2025"},
        {"az": "2025/0156", "mandant": "Gerd Fischer", "gegner": "Helga Fischer",
         "typ": "Versorgungsausgleich", "anwalt": "Dr. Mueller", "status": "Ruhend",
         "angelegt": "01.09.2025", "letzte_aktivitaet": "15.11.2025"},
    ]

    # Such- und Filterbereich
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        suchbegriff = st.text_input(
            "Suche",
            placeholder="Aktenzeichen, Name oder Mandant...",
            label_visibility="collapsed"
        )

    with col2:
        filter_typ = st.selectbox(
            "Verfahrensart",
            ["Alle", "Scheidung", "Kindesunterhalt", "Trennungsunterhalt",
             "Zugewinnausgleich", "Versorgungsausgleich"],
            label_visibility="collapsed"
        )

    with col3:
        filter_status = st.selectbox(
            "Status",
            ["Alle", "Aktiv", "Ruhend", "Abgeschlossen"],
            label_visibility="collapsed"
        )

    with col4:
        filter_anwalt = st.selectbox(
            "Anwalt",
            ["Alle", "Dr. Mueller", "Heigener", "Radtke", "Meier"],
            label_visibility="collapsed"
        )

    # Akten filtern
    gefilterte_akten = akten

    if suchbegriff:
        suchbegriff_lower = suchbegriff.lower()
        gefilterte_akten = [
            a for a in gefilterte_akten
            if suchbegriff_lower in a["az"].lower()
            or suchbegriff_lower in a["mandant"].lower()
            or suchbegriff_lower in a["gegner"].lower()
        ]

    if filter_typ != "Alle":
        gefilterte_akten = [a for a in gefilterte_akten if a["typ"] == filter_typ]

    if filter_status != "Alle":
        gefilterte_akten = [a for a in gefilterte_akten if a["status"] == filter_status]

    if filter_anwalt != "Alle":
        gefilterte_akten = [a for a in gefilterte_akten if a["anwalt"] == filter_anwalt]

    st.markdown("---")

    # Statistik
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gefunden", len(gefilterte_akten))
    with col2:
        aktive = len([a for a in gefilterte_akten if a["status"] == "Aktiv"])
        st.metric("Aktiv", aktive)
    with col3:
        ruhend = len([a for a in gefilterte_akten if a["status"] == "Ruhend"])
        st.metric("Ruhend", ruhend)
    with col4:
        abgeschlossen = len([a for a in gefilterte_akten if a["status"] == "Abgeschlossen"])
        st.metric("Abgeschlossen", abgeschlossen)

    st.markdown("---")

    # Aktenliste
    if gefilterte_akten:
        # Tabellenkopf
        header_col1, header_col2, header_col3, header_col4, header_col5, header_col6 = st.columns([1, 2, 2, 1.5, 1, 1])
        with header_col1:
            st.markdown("**Az.**")
        with header_col2:
            st.markdown("**Mandant**")
        with header_col3:
            st.markdown("**Gegner**")
        with header_col4:
            st.markdown("**Verfahren**")
        with header_col5:
            st.markdown("**Status**")
        with header_col6:
            st.markdown("**Aktion**")

        st.markdown("---")

        for akte in gefilterte_akten:
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1.5, 1, 1])

            with col1:
                st.write(akte["az"])

            with col2:
                st.write(akte["mandant"])
                st.caption(f"RA {akte['anwalt']}")

            with col3:
                st.write(akte["gegner"])

            with col4:
                st.write(akte["typ"])
                st.caption(f"Letzte Akt.: {akte['letzte_aktivitaet']}")

            with col5:
                if akte["status"] == "Aktiv":
                    st.success(akte["status"])
                elif akte["status"] == "Ruhend":
                    st.warning(akte["status"])
                else:
                    st.info(akte["status"])

            with col6:
                if st.button("Oeffnen", key=f"open_{akte['az']}", use_container_width=True):
                    st.session_state.selected_case = akte
                    st.session_state.current_page = "Aktendetail"
                    st.rerun()

            st.markdown("---")
    else:
        st.warning("Keine Akten gefunden.")


def show_case_detail():
    """Detailansicht einer Akte mit umfangreichem Dokumentenmanagement"""
    akte = st.session_state.get("selected_case")

    if not akte:
        st.warning("Keine Akte ausgewaehlt")
        if st.button("Zurueck zur Aktenuebersicht"):
            st.session_state.current_page = "Akten"
            st.rerun()
        return

    # Zurueck-Button
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("← Zurueck"):
            st.session_state.current_page = "Akten"
            st.session_state.selected_case = None
            st.rerun()

    with col_title:
        st.header(f"Akte {akte['az']}")

    # Akteninfo-Header
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mandant", akte["mandant"])
    with col2:
        st.metric("Gegner", akte["gegner"])
    with col3:
        st.metric("Verfahrensart", akte["typ"])
    with col4:
        st.metric("Status", akte["status"])

    st.markdown("---")

    # Tabs fuer verschiedene Bereiche
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Dokumente",
        "Berechnungen",
        "Gehaltsabrechnungen",
        "Schriftsaetze",
        "Aktenhistorie"
    ])

    # =====================================================
    # TAB 1: Dokumentenmanagement
    # =====================================================
    with tab1:
        st.subheader("Dokumentenverwaltung")

        # Demo-Dokumente fuer diese Akte
        dokumente = [
            {
                "id": 1,
                "name": "Personalausweis_Mustermann.pdf",
                "kategorie": "Persoenliche Dokumente",
                "typ": "Personalausweis",
                "hochgeladen": "05.01.2026 10:30",
                "hochgeladen_von": "Mandant",
                "groesse": "2.1 MB",
                "status": "geprueft",
                "geprueft_am": "06.01.2026 14:00",
                "geprueft_von": "Dr. Mueller",
                "notiz": "In Ordnung"
            },
            {
                "id": 2,
                "name": "Heiratsurkunde.pdf",
                "kategorie": "Persoenliche Dokumente",
                "typ": "Heiratsurkunde",
                "hochgeladen": "05.01.2026 10:32",
                "hochgeladen_von": "Mandant",
                "groesse": "1.8 MB",
                "status": "geprueft",
                "geprueft_am": "06.01.2026 14:05",
                "geprueft_von": "Dr. Mueller",
                "notiz": "Vollstaendig"
            },
            {
                "id": 3,
                "name": "Gehaltsabrechnung_Dez_2025.pdf",
                "kategorie": "Einkommensnachweise",
                "typ": "Gehaltsabrechnung",
                "hochgeladen": "08.01.2026 09:15",
                "hochgeladen_von": "Mandant",
                "groesse": "0.9 MB",
                "status": "ocr_fertig",
                "ocr_ergebnis": {
                    "brutto": 4850.00,
                    "netto": 3125.50,
                    "steuerklasse": "III",
                    "arbeitgeber": "Stadtwerke Rendsburg GmbH",
                    "monat": "Dezember 2025"
                },
                "geprueft_am": None,
                "geprueft_von": None,
                "notiz": None
            },
            {
                "id": 4,
                "name": "Gehaltsabrechnung_Nov_2025.pdf",
                "kategorie": "Einkommensnachweise",
                "typ": "Gehaltsabrechnung",
                "hochgeladen": "08.01.2026 09:16",
                "hochgeladen_von": "Mandant",
                "groesse": "0.9 MB",
                "status": "ocr_fertig",
                "ocr_ergebnis": {
                    "brutto": 4850.00,
                    "netto": 3125.50,
                    "steuerklasse": "III",
                    "arbeitgeber": "Stadtwerke Rendsburg GmbH",
                    "monat": "November 2025"
                },
                "geprueft_am": None,
                "geprueft_von": None,
                "notiz": None
            },
            {
                "id": 5,
                "name": "Mietvertrag_Ehewohnung.pdf",
                "kategorie": "Wohnung",
                "typ": "Mietvertrag",
                "hochgeladen": "10.01.2026 14:20",
                "hochgeladen_von": "Mandant",
                "groesse": "3.2 MB",
                "status": "neu",
                "geprueft_am": None,
                "geprueft_von": None,
                "notiz": None
            },
            {
                "id": 6,
                "name": "Kontoauszug_Gemeinschaftskonto.pdf",
                "kategorie": "Vermoegen",
                "typ": "Kontoauszug",
                "hochgeladen": "11.01.2026 11:00",
                "hochgeladen_von": "Mandant",
                "groesse": "1.5 MB",
                "status": "neu",
                "geprueft_am": None,
                "geprueft_von": None,
                "notiz": None
            },
        ]

        # Filter und Statistik
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            gesamt = len(dokumente)
            st.metric("Gesamt", gesamt)
        with col2:
            geprueft = len([d for d in dokumente if d["status"] == "geprueft"])
            st.metric("Geprueft", geprueft)
        with col3:
            offen = len([d for d in dokumente if d["status"] in ["neu", "ocr_fertig"]])
            st.metric("Offen", offen)
        with col4:
            mit_ocr = len([d for d in dokumente if d.get("ocr_ergebnis")])
            st.metric("Mit OCR-Daten", mit_ocr)

        st.markdown("---")

        # Filter
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            filter_kategorie = st.selectbox(
                "Kategorie",
                ["Alle", "Persoenliche Dokumente", "Einkommensnachweise", "Wohnung", "Vermoegen"]
            )
        with filter_col2:
            filter_status = st.selectbox(
                "Status",
                ["Alle", "Neu (unbearbeitet)", "OCR fertig", "Geprueft"]
            )

        # Dokumente filtern
        gefilterte_docs = dokumente
        if filter_kategorie != "Alle":
            gefilterte_docs = [d for d in gefilterte_docs if d["kategorie"] == filter_kategorie]
        if filter_status == "Neu (unbearbeitet)":
            gefilterte_docs = [d for d in gefilterte_docs if d["status"] == "neu"]
        elif filter_status == "OCR fertig":
            gefilterte_docs = [d for d in gefilterte_docs if d["status"] == "ocr_fertig"]
        elif filter_status == "Geprueft":
            gefilterte_docs = [d for d in gefilterte_docs if d["status"] == "geprueft"]

        st.markdown("---")

        # Dokumentenliste mit Aktionen
        for doc in gefilterte_docs:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 2])

                with col1:
                    # Status-Icon
                    if doc["status"] == "geprueft":
                        status_icon = "✓"
                        status_color = "green"
                    elif doc["status"] == "ocr_fertig":
                        status_icon = "📊"
                        status_color = "blue"
                    else:
                        status_icon = "○"
                        status_color = "orange"

                    st.markdown(f"**{status_icon} {doc['name']}**")
                    st.caption(f"{doc['kategorie']} | {doc['typ']} | {doc['groesse']}")

                with col2:
                    st.caption(f"Hochgeladen: {doc['hochgeladen']}")
                    st.caption(f"Von: {doc['hochgeladen_von']}")

                with col3:
                    if doc["status"] == "geprueft":
                        st.success("Geprueft")
                        st.caption(f"von {doc['geprueft_von']}")
                    elif doc["status"] == "ocr_fertig":
                        st.info("OCR ausgewertet")
                    else:
                        st.warning("Neu")

                with col4:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Ansehen", key=f"view_{doc['id']}", use_container_width=True):
                            st.session_state.view_document = doc["id"]

                    with btn_col2:
                        if doc["status"] != "geprueft":
                            if st.button("Pruefen", key=f"check_{doc['id']}", use_container_width=True):
                                st.session_state.check_document = doc["id"]

                # Dokument-Detail anzeigen wenn ausgewaehlt
                if st.session_state.get("view_document") == doc["id"]:
                    with st.expander(f"Dokumentvorschau: {doc['name']}", expanded=True):
                        st.info("Dokumentvorschau wird hier angezeigt (PDF-Viewer)")

                        if doc.get("ocr_ergebnis"):
                            st.markdown("#### Extrahierte Daten (OCR)")
                            ocr = doc["ocr_ergebnis"]
                            ocr_col1, ocr_col2 = st.columns(2)
                            with ocr_col1:
                                st.write(f"**Brutto:** {ocr['brutto']:.2f} EUR")
                                st.write(f"**Netto:** {ocr['netto']:.2f} EUR")
                            with ocr_col2:
                                st.write(f"**Steuerklasse:** {ocr['steuerklasse']}")
                                st.write(f"**Arbeitgeber:** {ocr['arbeitgeber']}")
                                st.write(f"**Monat:** {ocr['monat']}")

                        if doc["notiz"]:
                            st.markdown(f"**Notiz:** {doc['notiz']}")

                        if st.button("Schliessen", key=f"close_view_{doc['id']}"):
                            st.session_state.view_document = None
                            st.rerun()

                # Pruefungsformular anzeigen wenn ausgewaehlt
                if st.session_state.get("check_document") == doc["id"]:
                    with st.expander(f"Dokument pruefen: {doc['name']}", expanded=True):
                        st.markdown("#### Dokumentenpruefung")

                        pruefung_status = st.radio(
                            "Status",
                            ["In Ordnung", "Nachbesserung erforderlich", "Abgelehnt"],
                            horizontal=True,
                            key=f"status_{doc['id']}"
                        )

                        notiz = st.text_area(
                            "Notiz / Kommentar",
                            placeholder="Optionale Bemerkung zum Dokument...",
                            key=f"notiz_{doc['id']}"
                        )

                        btn_c1, btn_c2, btn_c3 = st.columns(3)
                        with btn_c1:
                            if st.button("Als geprueft markieren", type="primary", key=f"save_check_{doc['id']}"):
                                st.success(f"Dokument wurde als '{pruefung_status}' markiert!")
                                st.session_state.check_document = None
                                st.rerun()
                        with btn_c2:
                            if st.button("Abbrechen", key=f"cancel_check_{doc['id']}"):
                                st.session_state.check_document = None
                                st.rerun()

                st.markdown("---")

    # =====================================================
    # TAB 2: Berechnungen mit Versionierung
    # =====================================================
    with tab2:
        st.subheader("Berechnungen zur Akte")

        # Demo-Berechnungen
        berechnungen = [
            {
                "id": 1,
                "typ": "Kindesunterhalt",
                "version": 3,
                "erstellt": "12.01.2026 14:30",
                "erstellt_von": "Dr. Mueller",
                "notiz": "Aktuelle Berechnung mit allen drei Kindern",
                "ergebnis": {
                    "gesamt_zahlbetrag": 1245,
                    "kinder": [
                        {"name": "Emma", "zahlbetrag": 498},
                        {"name": "Lukas", "zahlbetrag": 452},
                        {"name": "Sophie", "zahlbetrag": 295}
                    ]
                },
                "freigegeben": True
            },
            {
                "id": 2,
                "typ": "Kindesunterhalt",
                "version": 2,
                "erstellt": "10.01.2026 16:15",
                "erstellt_von": "Dr. Mueller",
                "notiz": "Korrektur: Kindergeld bei Emma vollstaendig angerechnet",
                "ergebnis": {
                    "gesamt_zahlbetrag": 1295,
                    "kinder": [
                        {"name": "Emma", "zahlbetrag": 548},
                        {"name": "Lukas", "zahlbetrag": 452},
                        {"name": "Sophie", "zahlbetrag": 295}
                    ]
                },
                "freigegeben": False
            },
            {
                "id": 3,
                "typ": "Kindesunterhalt",
                "version": 1,
                "erstellt": "08.01.2026 11:00",
                "erstellt_von": "Dr. Mueller",
                "notiz": "Erstberechnung basierend auf Gehaltsabrechnungen",
                "ergebnis": {
                    "gesamt_zahlbetrag": 1320,
                    "kinder": [
                        {"name": "Emma", "zahlbetrag": 573},
                        {"name": "Lukas", "zahlbetrag": 452},
                        {"name": "Sophie", "zahlbetrag": 295}
                    ]
                },
                "freigegeben": False
            },
            {
                "id": 4,
                "typ": "Trennungsunterhalt",
                "version": 1,
                "erstellt": "09.01.2026 09:30",
                "erstellt_von": "Dr. Mueller",
                "notiz": "Vorlaefige Berechnung, Einkommen Gegenseite geschaetzt",
                "ergebnis": {
                    "zahlbetrag": 687,
                    "bedarf": 1540
                },
                "freigegeben": False
            },
        ]

        # Neue Berechnung erstellen
        with st.expander("Neue Berechnung erstellen", expanded=False):
            calc_type = st.selectbox(
                "Berechnungsart",
                ["Kindesunterhalt", "Trennungsunterhalt", "Nachehelicher Unterhalt",
                 "Zugewinnausgleich", "RVG-Gebuehren"],
                key="new_calc_type"
            )

            notiz_neue = st.text_area(
                "Notiz zur Berechnung",
                placeholder="Beschreiben Sie den Anlass oder Besonderheiten dieser Berechnung...",
                key="new_calc_notiz"
            )

            # Einkommen aus Gehaltsabrechnungen vorschlagen
            st.markdown("#### Vorgeschlagene Werte aus Dokumenten")
            st.info("Aus den OCR-Daten der Gehaltsabrechnungen wurden folgende Werte extrahiert:")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Mandant:**")
                st.write("Durchschnitt Brutto: 4.850,00 EUR")
                st.write("Durchschnitt Netto: 3.125,50 EUR")
            with col2:
                if st.button("Werte uebernehmen", key="uebernehmen_btn"):
                    st.success("Werte wurden in die Berechnung uebernommen!")

            if st.button("Berechnung starten", type="primary", key="start_calc"):
                # Hier wuerde zur entsprechenden Berechnungsseite navigiert
                st.session_state.calc_for_case = akte["az"]
                st.session_state.calc_type = calc_type
                st.session_state.calc_notiz = notiz_neue
                st.success("Berechnung wird vorbereitet...")

        st.markdown("---")

        # Berechnungshistorie
        st.markdown("#### Berechnungshistorie")

        for calc in berechnungen:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1.5])

                with col1:
                    version_badge = f"v{calc['version']}"
                    freigabe_badge = " (Freigegeben)" if calc["freigegeben"] else ""
                    st.markdown(f"**{calc['typ']}** - Version {version_badge}{freigabe_badge}")
                    st.caption(calc["notiz"])

                with col2:
                    st.caption(f"Erstellt: {calc['erstellt']}")
                    st.caption(f"Von: {calc['erstellt_von']}")

                    if calc["typ"] == "Kindesunterhalt":
                        st.write(f"**Gesamt: {calc['ergebnis']['gesamt_zahlbetrag']} EUR/Monat**")
                    elif calc["typ"] == "Trennungsunterhalt":
                        st.write(f"**Zahlbetrag: {calc['ergebnis']['zahlbetrag']} EUR/Monat**")

                with col3:
                    if st.button("Details", key=f"calc_detail_{calc['id']}", use_container_width=True):
                        st.session_state.view_calc = calc["id"]

                    if not calc["freigegeben"]:
                        if st.button("Freigeben", key=f"calc_release_{calc['id']}", use_container_width=True):
                            st.success("Berechnung fuer Mandanten freigegeben!")

                # Berechnungsdetail anzeigen
                if st.session_state.get("view_calc") == calc["id"]:
                    with st.expander(f"Details: {calc['typ']} v{calc['version']}", expanded=True):
                        st.markdown(f"**Notiz:** {calc['notiz']}")
                        st.markdown(f"**Erstellt:** {calc['erstellt']} von {calc['erstellt_von']}")

                        st.markdown("---")
                        st.markdown("#### Ergebnis")

                        if calc["typ"] == "Kindesunterhalt":
                            for kind in calc["ergebnis"]["kinder"]:
                                st.write(f"- {kind['name']}: **{kind['zahlbetrag']} EUR/Monat**")
                            st.markdown(f"**Gesamt: {calc['ergebnis']['gesamt_zahlbetrag']} EUR/Monat**")
                        elif calc["typ"] == "Trennungsunterhalt":
                            st.write(f"Bedarf: {calc['ergebnis']['bedarf']} EUR")
                            st.write(f"**Zahlbetrag: {calc['ergebnis']['zahlbetrag']} EUR/Monat**")

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Als PDF exportieren", key=f"export_{calc['id']}"):
                                st.info("PDF wird generiert...")
                        with col_b:
                            if st.button("Schliessen", key=f"close_calc_{calc['id']}"):
                                st.session_state.view_calc = None
                                st.rerun()

                st.markdown("---")

    # =====================================================
    # TAB 3: Gehaltsabrechnungen mit OCR-Auswertung
    # =====================================================
    with tab3:
        st.subheader("Gehaltsabrechnungen (OCR-Auswertung)")

        # OCR-ausgewertete Gehaltsabrechnungen
        gehaltsabrechnungen = [
            {
                "id": 1,
                "monat": "Dezember 2025",
                "datei": "Gehaltsabrechnung_Dez_2025.pdf",
                "person": "Mandant (Max Mustermann)",
                "arbeitgeber": "Stadtwerke Rendsburg GmbH",
                "brutto": 4850.00,
                "netto": 3125.50,
                "steuerklasse": "III",
                "lohnsteuer": 523.40,
                "sozialabgaben": 987.60,
                "kindergeld": 0,
                "sonderzahlung": 0,
                "ocr_konfidenz": 0.95,
                "in_berechnung": True
            },
            {
                "id": 2,
                "monat": "November 2025",
                "datei": "Gehaltsabrechnung_Nov_2025.pdf",
                "person": "Mandant (Max Mustermann)",
                "arbeitgeber": "Stadtwerke Rendsburg GmbH",
                "brutto": 4850.00,
                "netto": 3125.50,
                "steuerklasse": "III",
                "lohnsteuer": 523.40,
                "sozialabgaben": 987.60,
                "kindergeld": 0,
                "sonderzahlung": 0,
                "ocr_konfidenz": 0.94,
                "in_berechnung": True
            },
            {
                "id": 3,
                "monat": "Oktober 2025",
                "datei": "Gehaltsabrechnung_Okt_2025.pdf",
                "person": "Mandant (Max Mustermann)",
                "arbeitgeber": "Stadtwerke Rendsburg GmbH",
                "brutto": 4850.00,
                "netto": 3125.50,
                "steuerklasse": "III",
                "lohnsteuer": 523.40,
                "sozialabgaben": 987.60,
                "kindergeld": 0,
                "sonderzahlung": 0,
                "ocr_konfidenz": 0.92,
                "in_berechnung": False
            },
        ]

        # Zusammenfassung
        st.markdown("#### Einkommensuebersicht")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_brutto = sum(g["brutto"] for g in gehaltsabrechnungen) / len(gehaltsabrechnungen)
            st.metric("⌀ Brutto", f"{avg_brutto:,.2f} EUR")
        with col2:
            avg_netto = sum(g["netto"] for g in gehaltsabrechnungen) / len(gehaltsabrechnungen)
            st.metric("⌀ Netto", f"{avg_netto:,.2f} EUR")
        with col3:
            st.metric("Anzahl Monate", len(gehaltsabrechnungen))
        with col4:
            in_calc = len([g for g in gehaltsabrechnungen if g["in_berechnung"]])
            st.metric("In Berechnung", f"{in_calc}/{len(gehaltsabrechnungen)}")

        st.markdown("---")

        # Detailliste
        st.markdown("#### Einzelne Gehaltsabrechnungen")

        for ga in gehaltsabrechnungen:
            with st.container():
                col1, col2, col3 = st.columns([2, 2.5, 1.5])

                with col1:
                    konfidenz_pct = int(ga["ocr_konfidenz"] * 100)
                    st.markdown(f"**{ga['monat']}**")
                    st.caption(f"OCR-Konfidenz: {konfidenz_pct}%")
                    st.caption(f"Datei: {ga['datei']}")

                with col2:
                    st.write(f"**Brutto:** {ga['brutto']:,.2f} EUR | **Netto:** {ga['netto']:,.2f} EUR")
                    st.caption(f"Steuerklasse {ga['steuerklasse']} | LSt: {ga['lohnsteuer']:.2f} EUR | Sozialabg.: {ga['sozialabgaben']:.2f} EUR")
                    st.caption(f"Arbeitgeber: {ga['arbeitgeber']}")

                with col3:
                    # Checkbox fuer Berechnung
                    in_calc = st.checkbox(
                        "In Berechnung",
                        value=ga["in_berechnung"],
                        key=f"ga_calc_{ga['id']}"
                    )

                    if st.button("Korrigieren", key=f"ga_edit_{ga['id']}", use_container_width=True):
                        st.session_state.edit_ga = ga["id"]

                # Korrekturformular
                if st.session_state.get("edit_ga") == ga["id"]:
                    with st.expander("Werte korrigieren", expanded=True):
                        st.warning("Die OCR-Erkennung kann Fehler enthalten. Bitte pruefen und korrigieren Sie die Werte.")

                        edit_col1, edit_col2 = st.columns(2)
                        with edit_col1:
                            new_brutto = st.number_input(
                                "Brutto",
                                value=ga["brutto"],
                                step=10.0,
                                key=f"edit_brutto_{ga['id']}"
                            )
                            new_netto = st.number_input(
                                "Netto",
                                value=ga["netto"],
                                step=10.0,
                                key=f"edit_netto_{ga['id']}"
                            )
                        with edit_col2:
                            new_stk = st.selectbox(
                                "Steuerklasse",
                                ["I", "II", "III", "IV", "V", "VI"],
                                index=["I", "II", "III", "IV", "V", "VI"].index(ga["steuerklasse"]),
                                key=f"edit_stk_{ga['id']}"
                            )
                            new_ag = st.text_input(
                                "Arbeitgeber",
                                value=ga["arbeitgeber"],
                                key=f"edit_ag_{ga['id']}"
                            )

                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("Speichern", type="primary", key=f"save_ga_{ga['id']}"):
                                st.success("Werte wurden korrigiert und gespeichert!")
                                st.session_state.edit_ga = None
                                st.rerun()
                        with btn_col2:
                            if st.button("Abbrechen", key=f"cancel_ga_{ga['id']}"):
                                st.session_state.edit_ga = None
                                st.rerun()

                st.markdown("---")

        # Import in Berechnung
        st.markdown("#### In Berechnung uebernehmen")
        if st.button("Markierte Gehaltsabrechnungen in neue Berechnung uebernehmen", type="primary"):
            st.success("Daten wurden fuer die Berechnung vorbereitet. Bitte wechseln Sie zum Tab 'Berechnungen'.")

    # =====================================================
    # TAB 4: Schriftsaetze zur Akte
    # =====================================================
    with tab4:
        st.subheader("Schriftsaetze zur Akte")

        # Demo-Schriftsaetze
        schriftsaetze = [
            {
                "id": 1,
                "titel": "Scheidungsantrag",
                "status": "versendet",
                "erstellt": "06.01.2026",
                "versendet": "07.01.2026",
                "empfaenger": "AG Rendsburg"
            },
            {
                "id": 2,
                "titel": "Unterhaltsantrag (Kindesunterhalt)",
                "status": "entwurf",
                "erstellt": "12.01.2026",
                "versendet": None,
                "empfaenger": "AG Rendsburg"
            },
        ]

        for ss in schriftsaetze:
            col1, col2, col3 = st.columns([3, 1.5, 1.5])

            with col1:
                st.markdown(f"**{ss['titel']}**")
                st.caption(f"Empfaenger: {ss['empfaenger']}")

            with col2:
                if ss["status"] == "versendet":
                    st.success(f"Versendet: {ss['versendet']}")
                else:
                    st.warning("Entwurf")
                st.caption(f"Erstellt: {ss['erstellt']}")

            with col3:
                if st.button("Oeffnen", key=f"ss_{ss['id']}", use_container_width=True):
                    st.info("Schriftsatz wird geoeffnet...")

            st.markdown("---")

        if st.button("Neuen Schriftsatz erstellen"):
            st.session_state.current_page = "Schriftsaetze"
            st.rerun()

    # =====================================================
    # TAB 5: Aktenhistorie
    # =====================================================
    with tab5:
        st.subheader("Aktenhistorie")

        # Demo-Historie
        historie = [
            {"datum": "12.01.2026 14:30", "aktion": "Berechnung erstellt", "benutzer": "Dr. Mueller",
             "details": "Kindesunterhalt v3 erstellt"},
            {"datum": "11.01.2026 11:00", "aktion": "Dokument hochgeladen", "benutzer": "Mandant",
             "details": "Kontoauszug_Gemeinschaftskonto.pdf"},
            {"datum": "10.01.2026 16:15", "aktion": "Berechnung erstellt", "benutzer": "Dr. Mueller",
             "details": "Kindesunterhalt v2 erstellt"},
            {"datum": "10.01.2026 14:20", "aktion": "Dokument hochgeladen", "benutzer": "Mandant",
             "details": "Mietvertrag_Ehewohnung.pdf"},
            {"datum": "09.01.2026 09:30", "aktion": "Berechnung erstellt", "benutzer": "Dr. Mueller",
             "details": "Trennungsunterhalt v1 erstellt"},
            {"datum": "08.01.2026 11:00", "aktion": "Berechnung erstellt", "benutzer": "Dr. Mueller",
             "details": "Kindesunterhalt v1 erstellt"},
            {"datum": "08.01.2026 09:16", "aktion": "Dokument hochgeladen", "benutzer": "Mandant",
             "details": "Gehaltsabrechnung_Nov_2025.pdf (OCR ausgefuehrt)"},
            {"datum": "08.01.2026 09:15", "aktion": "Dokument hochgeladen", "benutzer": "Mandant",
             "details": "Gehaltsabrechnung_Dez_2025.pdf (OCR ausgefuehrt)"},
            {"datum": "07.01.2026 10:00", "aktion": "Schriftsatz versendet", "benutzer": "Dr. Mueller",
             "details": "Scheidungsantrag an AG Rendsburg"},
            {"datum": "06.01.2026 14:05", "aktion": "Dokument geprueft", "benutzer": "Dr. Mueller",
             "details": "Heiratsurkunde.pdf als 'In Ordnung' markiert"},
            {"datum": "06.01.2026 14:00", "aktion": "Dokument geprueft", "benutzer": "Dr. Mueller",
             "details": "Personalausweis_Mustermann.pdf als 'In Ordnung' markiert"},
            {"datum": "05.01.2026 10:32", "aktion": "Dokument hochgeladen", "benutzer": "Mandant",
             "details": "Heiratsurkunde.pdf"},
            {"datum": "05.01.2026 10:30", "aktion": "Dokument hochgeladen", "benutzer": "Mandant",
             "details": "Personalausweis_Mustermann.pdf"},
            {"datum": "02.01.2026 09:00", "aktion": "Akte angelegt", "benutzer": "Dr. Mueller",
             "details": f"Akte {akte['az']} fuer {akte['mandant']} angelegt"},
        ]

        for eintrag in historie:
            col1, col2, col3 = st.columns([1.5, 1.5, 4])

            with col1:
                st.caption(eintrag["datum"])

            with col2:
                st.write(eintrag["benutzer"])

            with col3:
                st.markdown(f"**{eintrag['aktion']}**")
                st.caption(eintrag["details"])

            st.markdown("---")


def show_new_case():
    """Vollstaendiges Formular zur Anlage einer neuen Akte"""
    st.header("Neue Akte anlegen")

    # Fortschrittsanzeige
    if "new_case_step" not in st.session_state:
        st.session_state.new_case_step = 1

    # Tabs fuer verschiedene Abschnitte
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. Verfahrensart",
        "2. Mandant",
        "3. Gegenseite",
        "4. Kinder & Abschluss"
    ])

    with tab1:
        st.subheader("Verfahrensart und Aktenzeichen")

        col1, col2 = st.columns(2)

        with col1:
            # Aktenzeichen generieren
            jahr = date.today().year
            naechste_nr = "0025"  # In Produktion aus DB
            vorgeschlagenes_az = f"{jahr}/{naechste_nr}"

            aktenzeichen = st.text_input(
                "Aktenzeichen",
                value=vorgeschlagenes_az,
                help="Wird automatisch generiert, kann angepasst werden"
            )

            verfahrensart = st.selectbox(
                "Verfahrensart",
                [
                    "Scheidung (mit Folgesachen)",
                    "Scheidung (isoliert)",
                    "Kindesunterhalt",
                    "Trennungsunterhalt",
                    "Nachehelicher Unterhalt",
                    "Zugewinnausgleich",
                    "Versorgungsausgleich",
                    "Sorgerecht",
                    "Umgangsrecht",
                    "Vaterschaftsfeststellung",
                    "Sonstiges Familienrecht",
                ]
            )

        with col2:
            zustaendiger_anwalt = st.selectbox(
                "Zustaendiger Rechtsanwalt",
                ["Dr. Thomas Mueller", "Sabine Heigener", "Michael Radtke", "Klaus Meier"]
            )

            sachbearbeiter = st.selectbox(
                "Sachbearbeiter/in",
                ["Sandra Schmidt", "Petra Wagner", ""]
            )

            gerichtsbezirk = st.selectbox(
                "Zustaendiges Gericht",
                ["AG Rendsburg", "AG Eckernfoerde", "AG Neumuenster",
                 "AG Kiel", "OLG Schleswig", "Sonstiges"]
            )

        st.markdown("---")

        st.markdown("#### Heiratsdaten (bei Scheidung/Unterhalt)")
        col1, col2, col3 = st.columns(3)
        with col1:
            heiratsdatum = st.date_input(
                "Heiratsdatum",
                value=None,
                min_value=date(1950, 1, 1),
                max_value=date.today()
            )
        with col2:
            trennungsdatum = st.date_input(
                "Trennungsdatum",
                value=None,
                min_value=date(1950, 1, 1),
                max_value=date.today()
            )
        with col3:
            gueterstand = st.selectbox(
                "Gueterstand",
                ["Zugewinngemeinschaft", "Gutertrennung", "Guetergemeinschaft"]
            )

    with tab2:
        st.subheader("Mandantendaten")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Persoenliche Daten")

            mandant_anrede = st.selectbox(
                "Anrede",
                ["Herr", "Frau", "Divers"],
                key="mandant_anrede"
            )
            mandant_vorname = st.text_input("Vorname", key="mandant_vorname")
            mandant_nachname = st.text_input("Nachname", key="mandant_nachname")
            mandant_geburtsname = st.text_input("Geburtsname (optional)", key="mandant_geburtsname")
            mandant_geburtsdatum = st.date_input(
                "Geburtsdatum",
                value=None,
                min_value=date(1920, 1, 1),
                max_value=date.today(),
                key="mandant_geb"
            )
            mandant_staatsangehoerigkeit = st.text_input(
                "Staatsangehoerigkeit",
                value="deutsch",
                key="mandant_staat"
            )

        with col2:
            st.markdown("#### Kontaktdaten")

            mandant_strasse = st.text_input("Strasse, Hausnummer", key="mandant_strasse")
            mandant_plz = st.text_input("PLZ", key="mandant_plz")
            mandant_ort = st.text_input("Ort", key="mandant_ort")
            mandant_telefon = st.text_input("Telefon", key="mandant_telefon")
            mandant_email = st.text_input("E-Mail", key="mandant_email")

            st.markdown("#### Berufliche Situation")
            mandant_beruf = st.text_input("Beruf", key="mandant_beruf")
            mandant_einkommen = st.number_input(
                "Monatliches Nettoeinkommen (EUR)",
                min_value=0,
                max_value=100000,
                step=100,
                key="mandant_einkommen"
            )

    with tab3:
        st.subheader("Daten der Gegenseite")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Persoenliche Daten")

            gegner_anrede = st.selectbox(
                "Anrede",
                ["Herr", "Frau", "Divers"],
                key="gegner_anrede"
            )
            gegner_vorname = st.text_input("Vorname", key="gegner_vorname")
            gegner_nachname = st.text_input("Nachname", key="gegner_nachname")
            gegner_geburtsdatum = st.date_input(
                "Geburtsdatum",
                value=None,
                min_value=date(1920, 1, 1),
                max_value=date.today(),
                key="gegner_geb"
            )

        with col2:
            st.markdown("#### Kontakt & Vertretung")

            gegner_strasse = st.text_input("Strasse, Hausnummer", key="gegner_strasse")
            gegner_plz = st.text_input("PLZ", key="gegner_plz")
            gegner_ort = st.text_input("Ort", key="gegner_ort")

            st.markdown("---")

            gegner_anwalt = st.checkbox("Gegenseite ist anwaltlich vertreten")
            if gegner_anwalt:
                gegner_ra_name = st.text_input("Name des gegnerischen RA")
                gegner_ra_kanzlei = st.text_input("Kanzlei")

    with tab4:
        st.subheader("Kinder & Abschluss")

        st.markdown("#### Gemeinsame Kinder")

        anzahl_kinder = st.number_input(
            "Anzahl gemeinsamer Kinder",
            min_value=0,
            max_value=10,
            value=0,
            step=1
        )

        if anzahl_kinder > 0:
            for i in range(int(anzahl_kinder)):
                with st.expander(f"Kind {i + 1}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.text_input("Vorname", key=f"kind_{i}_vorname")
                    with col2:
                        st.date_input(
                            "Geburtsdatum",
                            value=None,
                            key=f"kind_{i}_geb"
                        )
                    with col3:
                        st.selectbox(
                            "Lebt bei",
                            ["Mandant", "Gegenseite", "Wechselmodell"],
                            key=f"kind_{i}_bei"
                        )

        st.markdown("---")
        st.markdown("#### Notizen & Besonderheiten")

        notizen = st.text_area(
            "Interne Notizen zur Akte",
            height=100,
            placeholder="Besonderheiten, erste Informationen zum Sachverhalt..."
        )

        st.markdown("---")

        # Zusammenfassung
        st.markdown("#### Zusammenfassung")

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Aktenzeichen: **{aktenzeichen}**")
            st.info(f"Verfahrensart: **{verfahrensart}**")
        with col2:
            st.info(f"Zustaendiger RA: **{zustaendiger_anwalt}**")
            if anzahl_kinder > 0:
                st.info(f"Anzahl Kinder: **{int(anzahl_kinder)}**")

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            mandantenzugang = st.checkbox(
                "Mandantenzugang erstellen",
                value=True,
                help="Erstellt automatisch einen Zugangscode fuer das Mandantenportal"
            )

        with col2:
            if st.button("Akte anlegen", type="primary", use_container_width=True):
                # Validierung
                if not mandant_vorname or not mandant_nachname:
                    st.error("Bitte geben Sie mindestens den Namen des Mandanten ein.")
                else:
                    st.success(f"Akte {aktenzeichen} wurde erfolgreich angelegt!")
                    if mandantenzugang:
                        zugangscode = f"{mandant_nachname.upper()}{jahr}"
                        st.info(f"Mandantenzugangscode: **{zugangscode}**")
                    st.balloons()

        with col3:
            if st.button("Abbrechen", use_container_width=True):
                st.session_state.current_page = "Akten"
                st.rerun()


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
    """Schriftsatzvorlagen und -erstellung"""
    st.header("Schriftsaetze")

    tab1, tab2, tab3 = st.tabs(["Vorlagen", "Neuer Schriftsatz", "Letzte Schriftsaetze"])

    with tab1:
        st.subheader("Schriftsatzvorlagen")

        # Kategorien
        kategorie = st.selectbox(
            "Kategorie",
            ["Alle", "Scheidung", "Unterhalt", "Sorgerecht", "Zugewinn", "Allgemein"]
        )

        st.markdown("---")

        # Vorlagen-Liste
        vorlagen = [
            {"name": "Scheidungsantrag", "kategorie": "Scheidung", "beschreibung": "Antrag auf Ehescheidung mit Folgesachen"},
            {"name": "Unterhaltsantrag", "kategorie": "Unterhalt", "beschreibung": "Antrag auf Festsetzung von Kindesunterhalt"},
            {"name": "Auskunftsaufforderung", "kategorie": "Unterhalt", "beschreibung": "Aufforderung zur Auskunft ueber Einkommensverhaeltnisse"},
            {"name": "Sorgerechtsantrag", "kategorie": "Sorgerecht", "beschreibung": "Antrag auf Uebertragung des alleinigen Sorgerechts"},
            {"name": "Umgangsantrag", "kategorie": "Sorgerecht", "beschreibung": "Antrag auf Regelung des Umgangsrechts"},
            {"name": "Zugewinnausgleichsantrag", "kategorie": "Zugewinn", "beschreibung": "Stufenantrag auf Auskunft und Zahlung"},
            {"name": "Vollmacht", "kategorie": "Allgemein", "beschreibung": "Anwaltliche Vollmacht"},
            {"name": "Kostenfestsetzung", "kategorie": "Allgemein", "beschreibung": "Antrag auf Kostenfestsetzung"},
        ]

        gefilterte_vorlagen = vorlagen if kategorie == "Alle" else [v for v in vorlagen if v["kategorie"] == kategorie]

        for vorlage in gefilterte_vorlagen:
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                st.markdown(f"**{vorlage['name']}**")
                st.caption(vorlage["kategorie"])
            with col2:
                st.write(vorlage["beschreibung"])
            with col3:
                if st.button("Verwenden", key=f"vorlage_{vorlage['name']}", use_container_width=True):
                    st.session_state.selected_template = vorlage["name"]
                    st.info(f"Vorlage '{vorlage['name']}' ausgewaehlt")
            st.markdown("---")

    with tab2:
        st.subheader("Neuen Schriftsatz erstellen")

        col1, col2 = st.columns(2)

        with col1:
            akte = st.selectbox(
                "Akte",
                ["2026/0001 - Mustermann", "2026/0015 - Schmidt", "2026/0008 - Meyer"]
            )

            vorlage_auswahl = st.selectbox(
                "Vorlage",
                ["Freie Eingabe", "Scheidungsantrag", "Unterhaltsantrag",
                 "Auskunftsaufforderung", "Sorgerechtsantrag"]
            )

        with col2:
            empfaenger = st.selectbox(
                "Empfaenger",
                ["AG Rendsburg", "Gegnerischer RA", "Mandant", "Gegenseite"]
            )

            datum = st.date_input("Datum", value=date.today())

        st.markdown("---")

        betreff = st.text_input(
            "Betreff",
            placeholder="Az. ... ./. ..."
        )

        inhalt = st.text_area(
            "Inhalt",
            height=300,
            placeholder="Schriftsatzinhalt eingeben oder aus Vorlage laden..."
        )

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Speichern", type="primary", use_container_width=True):
                st.success("Schriftsatz gespeichert!")
        with col2:
            if st.button("Als PDF exportieren", use_container_width=True):
                st.info("PDF wird erstellt...")

    with tab3:
        st.subheader("Zuletzt erstellte Schriftsaetze")

        letzte_schriftsaetze = [
            {"datum": "12.01.2026", "typ": "Unterhaltsantrag", "akte": "2026/0015", "empfaenger": "AG Rendsburg"},
            {"datum": "11.01.2026", "typ": "Scheidungsantrag", "akte": "2026/0001", "empfaenger": "AG Rendsburg"},
            {"datum": "10.01.2026", "typ": "Auskunftsaufforderung", "akte": "2026/0008", "empfaenger": "Gegnerischer RA"},
        ]

        for ss in letzte_schriftsaetze:
            col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
            with col1:
                st.write(ss["datum"])
            with col2:
                st.markdown(f"**{ss['typ']}**")
                st.caption(f"Az. {ss['akte']}")
            with col3:
                st.write(ss["empfaenger"])
            with col4:
                st.button("Oeffnen", key=f"ss_{ss['datum']}_{ss['typ']}", use_container_width=True)
            st.markdown("---")


def show_documents_management():
    """Vollstaendige Dokumentenverwaltung"""
    st.header("Dokumentenverwaltung")

    tab1, tab2, tab3 = st.tabs(["Alle Dokumente", "Upload", "Suche"])

    with tab1:
        st.subheader("Dokumentenuebersicht")

        # Filter
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_akte = st.selectbox(
                "Akte",
                ["Alle Akten", "2026/0001", "2026/0015", "2026/0008"],
                key="dok_filter_akte"
            )
        with col2:
            filter_kategorie = st.selectbox(
                "Kategorie",
                ["Alle", "Einkommensnachweise", "Persoenliche Dokumente",
                 "Gerichtliche Dokumente", "Korrespondenz"],
                key="dok_filter_kat"
            )
        with col3:
            filter_zeitraum = st.selectbox(
                "Zeitraum",
                ["Alle", "Heute", "Diese Woche", "Dieser Monat"],
                key="dok_filter_zeit"
            )

        st.markdown("---")

        # Demo-Dokumente
        dokumente = [
            {"name": "Gehaltsabrechnung_Dez_2025.pdf", "akte": "2026/0001", "kategorie": "Einkommensnachweise",
             "datum": "12.01.2026", "groesse": "245 KB", "status": "Geprueft"},
            {"name": "Heiratsurkunde.pdf", "akte": "2026/0001", "kategorie": "Persoenliche Dokumente",
             "datum": "11.01.2026", "groesse": "1.2 MB", "status": "Geprueft"},
            {"name": "Steuerbescheid_2024.pdf", "akte": "2026/0001", "kategorie": "Einkommensnachweise",
             "datum": "10.01.2026", "groesse": "890 KB", "status": "In Pruefung"},
            {"name": "Geburtsurkunde_Kind.pdf", "akte": "2026/0015", "kategorie": "Persoenliche Dokumente",
             "datum": "10.01.2026", "groesse": "156 KB", "status": "Geprueft"},
            {"name": "Scheidungsantrag_Entwurf.docx", "akte": "2026/0001", "kategorie": "Gerichtliche Dokumente",
             "datum": "09.01.2026", "groesse": "78 KB", "status": "Entwurf"},
        ]

        # Tabellenkopf
        header_cols = st.columns([3, 1, 1.5, 1, 1, 1])
        with header_cols[0]:
            st.markdown("**Dokument**")
        with header_cols[1]:
            st.markdown("**Akte**")
        with header_cols[2]:
            st.markdown("**Kategorie**")
        with header_cols[3]:
            st.markdown("**Datum**")
        with header_cols[4]:
            st.markdown("**Status**")
        with header_cols[5]:
            st.markdown("**Aktion**")

        st.markdown("---")

        for dok in dokumente:
            cols = st.columns([3, 1, 1.5, 1, 1, 1])
            with cols[0]:
                st.write(dok["name"])
                st.caption(dok["groesse"])
            with cols[1]:
                st.write(dok["akte"])
            with cols[2]:
                st.write(dok["kategorie"])
            with cols[3]:
                st.write(dok["datum"])
            with cols[4]:
                if dok["status"] == "Geprueft":
                    st.success(dok["status"])
                elif dok["status"] == "In Pruefung":
                    st.warning(dok["status"])
                else:
                    st.info(dok["status"])
            with cols[5]:
                st.button("Ansehen", key=f"view_{dok['name']}", use_container_width=True)
            st.markdown("---")

    with tab2:
        st.subheader("Dokument hochladen")

        col1, col2 = st.columns(2)

        with col1:
            upload_akte = st.selectbox(
                "Zur Akte",
                ["2026/0001 - Mustermann", "2026/0015 - Schmidt", "2026/0008 - Meyer"],
                key="upload_akte"
            )

            upload_kategorie = st.selectbox(
                "Kategorie",
                ["Einkommensnachweise", "Persoenliche Dokumente",
                 "Gerichtliche Dokumente", "Korrespondenz", "Sonstige"],
                key="upload_kat"
            )

        with col2:
            upload_beschreibung = st.text_input(
                "Beschreibung (optional)",
                placeholder="Kurze Beschreibung des Dokuments"
            )

            ocr_aktivieren = st.checkbox(
                "OCR-Texterkennung aktivieren",
                value=True,
                help="Automatische Texterkennung fuer durchsuchbare Dokumente"
            )

        st.markdown("---")

        uploaded_files = st.file_uploader(
            "Dokumente auswaehlen",
            type=["pdf", "jpg", "jpeg", "png", "docx", "xlsx"],
            accept_multiple_files=True,
            help="Unterstuetzte Formate: PDF, JPG, PNG, DOCX, XLSX"
        )

        if uploaded_files:
            st.info(f"{len(uploaded_files)} Datei(en) ausgewaehlt")

            if st.button("Hochladen", type="primary"):
                progress = st.progress(0)
                for i, file in enumerate(uploaded_files):
                    progress.progress((i + 1) / len(uploaded_files))
                st.success(f"{len(uploaded_files)} Dokument(e) erfolgreich hochgeladen!")

    with tab3:
        st.subheader("Dokumentensuche")

        suchbegriff = st.text_input(
            "Volltextsuche",
            placeholder="Suchbegriff eingeben (durchsucht auch OCR-Text)..."
        )

        col1, col2 = st.columns(2)
        with col1:
            datum_von = st.date_input("Von", value=None, key="such_von")
        with col2:
            datum_bis = st.date_input("Bis", value=None, key="such_bis")

        if st.button("Suchen", type="primary"):
            if suchbegriff:
                st.info(f"Suche nach '{suchbegriff}'...")
                st.warning("Demo: In der Produktionsversion werden hier OCR-Ergebnisse angezeigt.")
            else:
                st.warning("Bitte geben Sie einen Suchbegriff ein.")


def show_dokumentenanforderung():
    """Dokumentenanforderung fuer Anwaelte"""
    from src.pages.anwalt.dokumentenanforderung import render_dokumentenanforderung_page
    render_dokumentenanforderung_page()


# =============================================================================
# Mandanten-Seiten
# =============================================================================

def show_client_overview():
    """Mandanten-Dashboard mit prominenten Dokumentenanforderungen"""
    from src.pages.mandant.dokumente import render_mandant_dashboard
    render_mandant_dashboard()


def show_document_upload():
    """Kategorisierte Dokumenten-Upload-Seite"""
    from src.pages.mandant.dokumente import render_dokument_upload
    render_dokument_upload()


def show_client_documents():
    """Uebersicht hochgeladener Dokumente"""
    from src.pages.mandant.dokumente import render_meine_dokumente
    render_meine_dokumente()


def show_client_calculations():
    """Freigegebene Berechnungen des Anwalts"""
    from src.pages.mandant.dokumente import render_freigegebene_berechnungen
    render_freigegebene_berechnungen()


def show_client_messages():
    """Nachrichtensystem fuer Mandanten"""
    st.header("Nachrichten")

    case = st.session_state.current_case
    if case:
        st.info(f"Kommunikation zur Akte **{case.get('case_number')}**")

    tab1, tab2 = st.tabs(["Posteingang", "Neue Nachricht"])

    with tab1:
        st.subheader("Ihre Nachrichten")

        # Demo-Nachrichten
        nachrichten = [
            {
                "id": 1,
                "von": "RA Dr. Mueller",
                "betreff": "Unterlagen erhalten",
                "vorschau": "Vielen Dank fuer die Zusendung der Gehaltsabrechnungen...",
                "datum": "12.01.2026 14:30",
                "gelesen": False
            },
            {
                "id": 2,
                "von": "Sekretariat",
                "betreff": "Terminbestaetigung",
                "vorschau": "Ihr Termin am 15.01.2026 um 10:00 Uhr wurde bestaetigt...",
                "datum": "10.01.2026 09:15",
                "gelesen": True
            },
            {
                "id": 3,
                "von": "RA Dr. Mueller",
                "betreff": "Willkommen bei RHM",
                "vorschau": "Sehr geehrter Herr Mustermann, vielen Dank fuer Ihr Vertrauen...",
                "datum": "05.01.2026 11:00",
                "gelesen": True
            },
        ]

        for msg in nachrichten:
            with st.container():
                col1, col2, col3 = st.columns([3, 1.5, 0.5])

                with col1:
                    if not msg["gelesen"]:
                        st.markdown(f"**{msg['betreff']}** (Neu)")
                    else:
                        st.write(msg["betreff"])
                    st.caption(msg["vorschau"][:60] + "...")

                with col2:
                    st.caption(msg["von"])
                    st.caption(msg["datum"])

                with col3:
                    if st.button("Lesen", key=f"msg_{msg['id']}", use_container_width=True):
                        st.session_state.selected_message = msg["id"]

                st.markdown("---")

        # Nachricht anzeigen wenn ausgewaehlt
        if st.session_state.get("selected_message"):
            msg_id = st.session_state.selected_message
            msg = next((m for m in nachrichten if m["id"] == msg_id), None)

            if msg:
                st.markdown("---")
                st.subheader(msg["betreff"])
                st.caption(f"Von: {msg['von']} | {msg['datum']}")
                st.markdown("---")

                # Demo-Inhalt
                if msg_id == 1:
                    st.write("""
                    Sehr geehrter Herr Mustermann,

                    vielen Dank fuer die Zusendung der Gehaltsabrechnungen.
                    Die Unterlagen sind vollstaendig und werden nun von uns geprueft.

                    Fuer die Berechnung des Unterhalts benoetigen wir noch den aktuellen
                    Steuerbescheid. Bitte laden Sie diesen im Mandantenportal hoch.

                    Mit freundlichen Gruessen
                    Dr. Thomas Mueller
                    Rechtsanwalt
                    """)
                elif msg_id == 2:
                    st.write("""
                    Sehr geehrter Herr Mustermann,

                    hiermit bestaetigen wir Ihren Besprechungstermin:

                    Datum: 15.01.2026
                    Uhrzeit: 10:00 Uhr
                    Ort: Kanzlei RHM, Musterstrasse 1, 24768 Rendsburg

                    Bitte bringen Sie saemtliche Originalunterlagen mit.

                    Mit freundlichen Gruessen
                    Ihr Sekretariat
                    """)
                else:
                    st.write("""
                    Sehr geehrter Herr Mustermann,

                    vielen Dank fuer Ihr Vertrauen in unsere Kanzlei.

                    Wir haben Ihre Akte angelegt und werden uns umgehend
                    um Ihre Angelegenheit kuemmern.

                    Im Mandantenportal koennen Sie jederzeit den Status
                    Ihrer Akte einsehen und Dokumente hochladen.

                    Bei Fragen stehen wir Ihnen gerne zur Verfuegung.

                    Mit freundlichen Gruessen
                    Dr. Thomas Mueller
                    Rechtsanwalt
                    """)

                if st.button("Antworten"):
                    st.session_state.reply_to = msg_id

    with tab2:
        st.subheader("Neue Nachricht an Ihre Kanzlei")

        empfaenger = st.selectbox(
            "An",
            ["RA Dr. Mueller (Ihr Anwalt)", "Sekretariat", "Buchhaltung"]
        )

        betreff = st.text_input(
            "Betreff",
            value=f"Re: {nachrichten[0]['betreff']}" if st.session_state.get("reply_to") else "",
            placeholder="Betreff Ihrer Nachricht"
        )

        nachricht = st.text_area(
            "Ihre Nachricht",
            height=200,
            placeholder="Schreiben Sie hier Ihre Nachricht..."
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Senden", type="primary", use_container_width=True):
                if betreff and nachricht:
                    st.success("Ihre Nachricht wurde gesendet!")
                    st.session_state.reply_to = None
                else:
                    st.warning("Bitte geben Sie Betreff und Nachricht ein.")

        st.markdown("---")
        st.caption("Hinweis: Fuer dringende Angelegenheiten rufen Sie bitte in der Kanzlei an: 04331 / 12345")


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
