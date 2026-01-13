"""
Authentifizierungs-Service fuer FamilyKom

Bietet:
- Benutzer-Authentifizierung (Login/Logout)
- Passwort-Management (Hash, Verify, Reset)
- Session-Verwaltung
- Supabase-Integration (wenn konfiguriert)
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
import bcrypt
import jwt

# Supabase (optional)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


@dataclass
class Benutzer:
    """Repraesentiert einen Benutzer"""
    id: str
    benutzername: str
    email: str
    rolle: str
    vorname: str = ""
    nachname: str = ""
    titel: str = ""
    aktiv: bool = True
    email_verifiziert: bool = False
    letzter_login: Optional[datetime] = None
    erstellt_am: Optional[datetime] = None
    berechtigungen: Dict = field(default_factory=dict)


@dataclass
class AuthErgebnis:
    """Ergebnis eines Authentifizierungsversuchs"""
    erfolgreich: bool
    benutzer: Optional[Benutzer] = None
    token: Optional[str] = None
    fehler: Optional[str] = None
    muss_passwort_aendern: bool = False


class AuthService:
    """
    Authentifizierungs-Service

    Unterstuetzt zwei Modi:
    1. Demo-Modus: Fest codierte Benutzer fuer Tests
    2. Produktions-Modus: Supabase-Integration
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialisiert den Auth-Service

        Args:
            supabase_url: Supabase-URL (optional)
            supabase_key: Supabase-API-Key (optional)
        """
        self.supabase_client = None
        self.demo_modus = True
        self.jwt_secret = secrets.token_hex(32)
        self.session_dauer = timedelta(hours=8)

        # Supabase initialisieren wenn verfuegbar
        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            try:
                self.supabase_client = create_client(supabase_url, supabase_key)
                self.demo_modus = False
            except Exception as e:
                print(f"Supabase-Initialisierung fehlgeschlagen: {e}")
                self.demo_modus = True

        # Demo-Benutzer
        self._demo_benutzer = self._erstelle_demo_benutzer()

        # Fehlgeschlagene Login-Versuche tracken
        self._login_versuche: Dict[str, list] = {}
        self._max_versuche = 5
        self._sperrzeit = timedelta(minutes=15)

    def _erstelle_demo_benutzer(self) -> Dict[str, Dict]:
        """Erstellt Demo-Benutzer fuer Test-Zwecke"""
        return {
            # Administratoren
            "admin": {
                "id": "admin-001",
                "benutzername": "admin",
                "passwort_hash": self._hash_passwort("admin123"),
                "email": "admin@kanzlei-rhm.de",
                "rolle": "admin",
                "vorname": "System",
                "nachname": "Administrator",
                "titel": "",
                "aktiv": True,
                "email_verifiziert": True,
                "berechtigungen": {"admin": True, "alle": True}
            },
            # Anwaelte
            "mueller": {
                "id": "anwalt-001",
                "benutzername": "mueller",
                "passwort_hash": self._hash_passwort("anwalt123"),
                "email": "mueller@kanzlei-rhm.de",
                "rolle": "anwalt",
                "vorname": "Thomas",
                "nachname": "Mueller",
                "titel": "Dr.",
                "aktiv": True,
                "email_verifiziert": True,
                "berechtigungen": {
                    "akten_lesen": True,
                    "akten_schreiben": True,
                    "akten_loeschen": True,
                    "berechnungen": True,
                    "freigabe": True
                }
            },
            "heigener": {
                "id": "anwalt-002",
                "benutzername": "heigener",
                "passwort_hash": self._hash_passwort("anwalt123"),
                "email": "heigener@kanzlei-rhm.de",
                "rolle": "anwalt",
                "vorname": "Sabine",
                "nachname": "Heigener",
                "titel": "",
                "aktiv": True,
                "email_verifiziert": True,
                "berechtigungen": {
                    "akten_lesen": True,
                    "akten_schreiben": True,
                    "akten_loeschen": True,
                    "berechnungen": True,
                    "freigabe": True
                }
            },
            "radtke": {
                "id": "anwalt-003",
                "benutzername": "radtke",
                "passwort_hash": self._hash_passwort("anwalt123"),
                "email": "radtke@kanzlei-rhm.de",
                "rolle": "anwalt",
                "vorname": "Michael",
                "nachname": "Radtke",
                "titel": "",
                "aktiv": True,
                "email_verifiziert": True,
                "berechtigungen": {
                    "akten_lesen": True,
                    "akten_schreiben": True,
                    "akten_loeschen": True,
                    "berechnungen": True,
                    "freigabe": True
                }
            },
            "meier": {
                "id": "anwalt-004",
                "benutzername": "meier",
                "passwort_hash": self._hash_passwort("anwalt123"),
                "email": "meier@kanzlei-rhm.de",
                "rolle": "anwalt",
                "vorname": "Klaus",
                "nachname": "Meier",
                "titel": "",
                "aktiv": True,
                "email_verifiziert": True,
                "berechtigungen": {
                    "akten_lesen": True,
                    "akten_schreiben": True,
                    "akten_loeschen": True,
                    "berechnungen": True,
                    "freigabe": True
                }
            },
            # Mitarbeiter
            "schmidt": {
                "id": "ma-001",
                "benutzername": "schmidt",
                "passwort_hash": self._hash_passwort("mitarbeiter123"),
                "email": "schmidt@kanzlei-rhm.de",
                "rolle": "mitarbeiter",
                "vorname": "Sandra",
                "nachname": "Schmidt",
                "titel": "",
                "aktiv": True,
                "email_verifiziert": True,
                "berechtigungen": {
                    "akten_lesen": True,
                    "akten_schreiben": True,
                    "berechnungen": True
                }
            },
            "wagner": {
                "id": "ma-002",
                "benutzername": "wagner",
                "passwort_hash": self._hash_passwort("mitarbeiter123"),
                "email": "wagner@kanzlei-rhm.de",
                "rolle": "mitarbeiter",
                "vorname": "Petra",
                "nachname": "Wagner",
                "titel": "",
                "aktiv": True,
                "email_verifiziert": True,
                "berechtigungen": {
                    "akten_lesen": True,
                    "akten_schreiben": True,
                    "berechnungen": True
                }
            }
        }

    def _hash_passwort(self, passwort: str) -> str:
        """Hasht ein Passwort mit bcrypt"""
        return bcrypt.hashpw(passwort.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_passwort(self, passwort: str, passwort_hash: str) -> bool:
        """Verifiziert ein Passwort gegen einen Hash"""
        try:
            return bcrypt.checkpw(passwort.encode('utf-8'), passwort_hash.encode('utf-8'))
        except Exception:
            return False

    def _ist_gesperrt(self, benutzername: str) -> Tuple[bool, Optional[int]]:
        """
        Prueft ob ein Benutzer wegen zu vieler Fehlversuche gesperrt ist

        Returns:
            Tuple (ist_gesperrt, verbleibende_sekunden)
        """
        if benutzername not in self._login_versuche:
            return False, None

        versuche = self._login_versuche[benutzername]

        # Alte Versuche entfernen
        jetzt = time.time()
        versuche = [v for v in versuche if jetzt - v < self._sperrzeit.total_seconds()]
        self._login_versuche[benutzername] = versuche

        if len(versuche) >= self._max_versuche:
            letzter_versuch = max(versuche)
            verbleibend = int(self._sperrzeit.total_seconds() - (jetzt - letzter_versuch))
            return True, verbleibend

        return False, None

    def _registriere_fehlversuch(self, benutzername: str):
        """Registriert einen fehlgeschlagenen Login-Versuch"""
        if benutzername not in self._login_versuche:
            self._login_versuche[benutzername] = []
        self._login_versuche[benutzername].append(time.time())

    def _erstelle_token(self, benutzer: Benutzer) -> str:
        """Erstellt einen JWT-Token fuer einen Benutzer"""
        payload = {
            "user_id": benutzer.id,
            "benutzername": benutzer.benutzername,
            "rolle": benutzer.rolle,
            "exp": datetime.utcnow() + self.session_dauer
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def _verifiziere_token(self, token: str) -> Optional[Dict]:
        """Verifiziert einen JWT-Token"""
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def login(self, benutzername: str, passwort: str) -> AuthErgebnis:
        """
        Authentifiziert einen Benutzer

        Args:
            benutzername: Benutzername oder E-Mail
            passwort: Passwort

        Returns:
            AuthErgebnis mit Benutzer und Token bei Erfolg
        """
        benutzername = benutzername.lower().strip()

        # Sperrung pruefen
        ist_gesperrt, verbleibend = self._ist_gesperrt(benutzername)
        if ist_gesperrt:
            return AuthErgebnis(
                erfolgreich=False,
                fehler=f"Konto gesperrt. Bitte warten Sie {verbleibend // 60} Minuten."
            )

        # Demo-Modus
        if self.demo_modus:
            return self._login_demo(benutzername, passwort)

        # Supabase-Login
        return self._login_supabase(benutzername, passwort)

    def _login_demo(self, benutzername: str, passwort: str) -> AuthErgebnis:
        """Login im Demo-Modus"""
        if benutzername not in self._demo_benutzer:
            self._registriere_fehlversuch(benutzername)
            return AuthErgebnis(
                erfolgreich=False,
                fehler="Benutzername oder Passwort falsch"
            )

        benutzer_data = self._demo_benutzer[benutzername]

        if not self._verify_passwort(passwort, benutzer_data["passwort_hash"]):
            self._registriere_fehlversuch(benutzername)
            return AuthErgebnis(
                erfolgreich=False,
                fehler="Benutzername oder Passwort falsch"
            )

        if not benutzer_data["aktiv"]:
            return AuthErgebnis(
                erfolgreich=False,
                fehler="Dieses Konto wurde deaktiviert"
            )

        # Benutzer-Objekt erstellen
        benutzer = Benutzer(
            id=benutzer_data["id"],
            benutzername=benutzer_data["benutzername"],
            email=benutzer_data["email"],
            rolle=benutzer_data["rolle"],
            vorname=benutzer_data["vorname"],
            nachname=benutzer_data["nachname"],
            titel=benutzer_data.get("titel", ""),
            aktiv=benutzer_data["aktiv"],
            email_verifiziert=benutzer_data["email_verifiziert"],
            letzter_login=datetime.now(),
            berechtigungen=benutzer_data.get("berechtigungen", {})
        )

        token = self._erstelle_token(benutzer)

        # Login-Versuche zuruecksetzen
        if benutzername in self._login_versuche:
            del self._login_versuche[benutzername]

        return AuthErgebnis(
            erfolgreich=True,
            benutzer=benutzer,
            token=token
        )

    def _login_supabase(self, benutzername: str, passwort: str) -> AuthErgebnis:
        """Login mit Supabase"""
        if not self.supabase_client:
            return AuthErgebnis(
                erfolgreich=False,
                fehler="Supabase nicht konfiguriert"
            )

        try:
            # Supabase Auth verwenden
            response = self.supabase_client.auth.sign_in_with_password({
                "email": benutzername if "@" in benutzername else f"{benutzername}@kanzlei-rhm.de",
                "password": passwort
            })

            if response.user:
                # Benutzer-Profil aus Datenbank laden
                profile = self.supabase_client.table("profiles").select("*").eq(
                    "id", response.user.id
                ).single().execute()

                benutzer = Benutzer(
                    id=response.user.id,
                    benutzername=profile.data.get("benutzername", ""),
                    email=response.user.email,
                    rolle=profile.data.get("rolle", "mandant"),
                    vorname=profile.data.get("vorname", ""),
                    nachname=profile.data.get("nachname", ""),
                    titel=profile.data.get("titel", ""),
                    aktiv=profile.data.get("aktiv", True),
                    email_verifiziert=response.user.email_confirmed_at is not None,
                    letzter_login=datetime.now()
                )

                return AuthErgebnis(
                    erfolgreich=True,
                    benutzer=benutzer,
                    token=response.session.access_token
                )

        except Exception as e:
            self._registriere_fehlversuch(benutzername)
            return AuthErgebnis(
                erfolgreich=False,
                fehler="Benutzername oder Passwort falsch"
            )

        return AuthErgebnis(
            erfolgreich=False,
            fehler="Unbekannter Fehler"
        )

    def login_mandant(self, zugangscode: str) -> AuthErgebnis:
        """
        Authentifiziert einen Mandanten mit Zugangscode

        Args:
            zugangscode: Der Mandanten-Zugangscode

        Returns:
            AuthErgebnis
        """
        zugangscode = zugangscode.upper().strip()

        # Demo-Zugangscodes
        demo_codes = {
            "MUSTERMANN2026": {
                "id": "mandant-001",
                "benutzername": "mandant_mustermann",
                "email": "max.mustermann@email.de",
                "vorname": "Max",
                "nachname": "Mustermann",
                "akte": "2026/0001"
            },
            "SCHMIDT2026": {
                "id": "mandant-002",
                "benutzername": "mandant_schmidt",
                "email": "maria.schmidt@email.de",
                "vorname": "Maria",
                "nachname": "Schmidt",
                "akte": "2026/0002"
            },
            "DEMO123456": {
                "id": "mandant-demo",
                "benutzername": "demo_mandant",
                "email": "demo@example.com",
                "vorname": "Demo",
                "nachname": "Benutzer",
                "akte": "2026/0001"
            }
        }

        if zugangscode not in demo_codes:
            return AuthErgebnis(
                erfolgreich=False,
                fehler="Ungueltiger Zugangscode"
            )

        mandant_data = demo_codes[zugangscode]

        benutzer = Benutzer(
            id=mandant_data["id"],
            benutzername=mandant_data["benutzername"],
            email=mandant_data["email"],
            rolle="mandant",
            vorname=mandant_data["vorname"],
            nachname=mandant_data["nachname"],
            aktiv=True,
            letzter_login=datetime.now(),
            berechtigungen={
                "eigene_akte": mandant_data["akte"],
                "dokumente_hochladen": True,
                "berechnungen_ansehen": True
            }
        )

        token = self._erstelle_token(benutzer)

        return AuthErgebnis(
            erfolgreich=True,
            benutzer=benutzer,
            token=token
        )

    def logout(self, token: str = None) -> bool:
        """
        Meldet einen Benutzer ab

        Args:
            token: Optional JWT-Token zum Invalidieren

        Returns:
            True bei Erfolg
        """
        if not self.demo_modus and self.supabase_client:
            try:
                self.supabase_client.auth.sign_out()
            except Exception:
                pass

        return True

    def passwort_aendern(self, benutzer_id: str, altes_passwort: str, neues_passwort: str) -> Tuple[bool, str]:
        """
        Aendert das Passwort eines Benutzers

        Args:
            benutzer_id: ID des Benutzers
            altes_passwort: Aktuelles Passwort
            neues_passwort: Neues Passwort

        Returns:
            Tuple (erfolg, nachricht)
        """
        # Passwort-Validierung
        if len(neues_passwort) < 8:
            return False, "Das Passwort muss mindestens 8 Zeichen lang sein"

        if not any(c.isupper() for c in neues_passwort):
            return False, "Das Passwort muss mindestens einen Grossbuchstaben enthalten"

        if not any(c.isdigit() for c in neues_passwort):
            return False, "Das Passwort muss mindestens eine Ziffer enthalten"

        if self.demo_modus:
            # Im Demo-Modus nur simulieren
            return True, "Passwort wurde geaendert (Demo-Modus)"

        # Supabase Passwort-Aenderung
        if self.supabase_client:
            try:
                self.supabase_client.auth.update_user({
                    "password": neues_passwort
                })
                return True, "Passwort wurde erfolgreich geaendert"
            except Exception as e:
                return False, f"Fehler beim Aendern des Passworts: {str(e)}"

        return False, "Passwort-Aenderung nicht moeglich"

    def passwort_zuruecksetzen(self, email: str) -> Tuple[bool, str]:
        """
        Sendet eine Passwort-Zuruecksetzungs-E-Mail

        Args:
            email: E-Mail-Adresse des Benutzers

        Returns:
            Tuple (erfolg, nachricht)
        """
        if self.demo_modus:
            return True, f"Passwort-Reset-Link wurde an {email} gesendet (Demo-Modus)"

        if self.supabase_client:
            try:
                self.supabase_client.auth.reset_password_email(email)
                return True, f"Passwort-Reset-Link wurde an {email} gesendet"
            except Exception as e:
                return False, f"Fehler: {str(e)}"

        return False, "Passwort-Reset nicht moeglich"

    def hat_berechtigung(self, benutzer: Benutzer, berechtigung: str) -> bool:
        """
        Prueft ob ein Benutzer eine bestimmte Berechtigung hat

        Args:
            benutzer: Benutzer-Objekt
            berechtigung: Name der Berechtigung

        Returns:
            True wenn berechtigt
        """
        if benutzer.rolle == "admin":
            return True

        return benutzer.berechtigungen.get(berechtigung, False)


# Globale Instanz
_auth_service = None


def get_auth_service() -> AuthService:
    """Gibt die globale AuthService-Instanz zurueck"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
