"""
E-Mail-Service fuer Benachrichtigungen

Unterstuetzt SMTP und Resend API fuer den Versand von E-Mails.
Im Demo-Modus werden E-Mails nur simuliert.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Optionaler Resend Import
try:
    import resend
    RESEND_VERFUEGBAR = True
except ImportError:
    RESEND_VERFUEGBAR = False


class EmailPrioritaet(Enum):
    """E-Mail Prioritaet"""
    NIEDRIG = "low"
    NORMAL = "normal"
    HOCH = "high"


class EmailTyp(Enum):
    """Vordefinierte E-Mail-Typen"""
    WILLKOMMEN = "willkommen"
    PASSWORT_RESET = "passwort_reset"
    NEUE_AKTE = "neue_akte"
    DOKUMENT_HOCHGELADEN = "dokument_hochgeladen"
    TERMIN_ERINNERUNG = "termin_erinnerung"
    FRIST_WARNUNG = "frist_warnung"
    BERECHNUNG_FERTIG = "berechnung_fertig"
    MANDANTEN_EINLADUNG = "mandanten_einladung"
    SYSTEM_BENACHRICHTIGUNG = "system"


@dataclass
class EmailAnhang:
    """E-Mail Anhang"""
    dateiname: str
    inhalt: bytes
    mime_type: str = "application/octet-stream"


@dataclass
class EmailErgebnis:
    """Ergebnis eines E-Mail-Versands"""
    erfolg: bool
    message_id: Optional[str] = None
    fehler: Optional[str] = None
    empfaenger: str = ""
    zeitstempel: datetime = field(default_factory=datetime.now)


@dataclass
class EmailNachricht:
    """E-Mail Nachricht"""
    empfaenger: Union[str, List[str]]
    betreff: str
    text_inhalt: str
    html_inhalt: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    anhaenge: List[EmailAnhang] = field(default_factory=list)
    prioritaet: EmailPrioritaet = EmailPrioritaet.NORMAL
    antwort_an: Optional[str] = None


class EmailVorlagen:
    """Vordefinierte E-Mail-Vorlagen fuer FamilyKom"""

    KANZLEI_NAME = "RHM Rechtsanwaelte"
    KANZLEI_EMAIL = "kanzlei@rhm-rendsburg.de"

    @staticmethod
    def willkommen(name: str, benutzername: str, temp_passwort: str = None) -> EmailNachricht:
        """Willkommens-E-Mail fuer neue Benutzer"""
        betreff = f"Willkommen bei FamilyKom - {EmailVorlagen.KANZLEI_NAME}"

        text = f"""
Sehr geehrte(r) {name},

herzlich willkommen bei FamilyKom, dem Mandantenportal von {EmailVorlagen.KANZLEI_NAME}.

Ihr Benutzername: {benutzername}
"""
        if temp_passwort:
            text += f"Ihr temporaeres Passwort: {temp_passwort}\n"
            text += "\nBitte aendern Sie Ihr Passwort nach dem ersten Login.\n"

        text += f"""
Sie koennen sich unter folgender Adresse anmelden:
https://familykom.rhm-rendsburg.de

Bei Fragen stehen wir Ihnen gerne zur Verfuegung.

Mit freundlichen Gruessen
{EmailVorlagen.KANZLEI_NAME}
"""

        html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
<h2 style="color: #2c5282;">Willkommen bei FamilyKom</h2>
<p>Sehr geehrte(r) {name},</p>
<p>herzlich willkommen bei FamilyKom, dem Mandantenportal von <strong>{EmailVorlagen.KANZLEI_NAME}</strong>.</p>
<div style="background: #f0f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;">
<p><strong>Ihr Benutzername:</strong> {benutzername}</p>
{'<p><strong>Temporaeres Passwort:</strong> ' + temp_passwort + '</p><p style="color: #c53030;"><em>Bitte aendern Sie Ihr Passwort nach dem ersten Login.</em></p>' if temp_passwort else ''}
</div>
<p>Sie koennen sich unter folgender Adresse anmelden:<br>
<a href="https://familykom.rhm-rendsburg.de" style="color: #2c5282;">https://familykom.rhm-rendsburg.de</a></p>
<p>Bei Fragen stehen wir Ihnen gerne zur Verfuegung.</p>
<p>Mit freundlichen Gruessen<br>
<strong>{EmailVorlagen.KANZLEI_NAME}</strong></p>
</body>
</html>
"""
        return EmailNachricht(
            empfaenger="",  # Wird beim Versand gesetzt
            betreff=betreff,
            text_inhalt=text,
            html_inhalt=html
        )

    @staticmethod
    def passwort_reset(name: str, reset_link: str) -> EmailNachricht:
        """Passwort-Reset E-Mail"""
        betreff = f"Passwort zuruecksetzen - {EmailVorlagen.KANZLEI_NAME}"

        text = f"""
Sehr geehrte(r) {name},

Sie haben das Zuruecksetzen Ihres Passworts angefordert.

Klicken Sie auf den folgenden Link, um ein neues Passwort zu setzen:
{reset_link}

Dieser Link ist 24 Stunden gueltig.

Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie bitte diese E-Mail.

Mit freundlichen Gruessen
{EmailVorlagen.KANZLEI_NAME}
"""

        html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
<h2 style="color: #2c5282;">Passwort zuruecksetzen</h2>
<p>Sehr geehrte(r) {name},</p>
<p>Sie haben das Zuruecksetzen Ihres Passworts angefordert.</p>
<p style="margin: 25px 0;">
<a href="{reset_link}" style="background: #2c5282; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px;">Neues Passwort setzen</a>
</p>
<p><small>Dieser Link ist 24 Stunden gueltig.</small></p>
<p style="color: #718096;"><em>Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie bitte diese E-Mail.</em></p>
<p>Mit freundlichen Gruessen<br>
<strong>{EmailVorlagen.KANZLEI_NAME}</strong></p>
</body>
</html>
"""
        return EmailNachricht(
            empfaenger="",
            betreff=betreff,
            text_inhalt=text,
            html_inhalt=html
        )

    @staticmethod
    def neue_akte(mandant_name: str, aktenzeichen: str, anwalt_name: str) -> EmailNachricht:
        """Benachrichtigung ueber neue Akte"""
        betreff = f"Neue Akte angelegt - {aktenzeichen}"

        text = f"""
Sehr geehrte(r) {mandant_name},

fuer Sie wurde eine neue Akte angelegt.

Aktenzeichen: {aktenzeichen}
Zustaendiger Anwalt: {anwalt_name}

Sie koennen alle Informationen zu Ihrer Akte in unserem Mandantenportal einsehen:
https://familykom.rhm-rendsburg.de

Mit freundlichen Gruessen
{EmailVorlagen.KANZLEI_NAME}
"""

        html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
<h2 style="color: #2c5282;">Neue Akte angelegt</h2>
<p>Sehr geehrte(r) {mandant_name},</p>
<p>fuer Sie wurde eine neue Akte angelegt.</p>
<div style="background: #f0f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;">
<p><strong>Aktenzeichen:</strong> {aktenzeichen}</p>
<p><strong>Zustaendiger Anwalt:</strong> {anwalt_name}</p>
</div>
<p>Sie koennen alle Informationen zu Ihrer Akte in unserem <a href="https://familykom.rhm-rendsburg.de" style="color: #2c5282;">Mandantenportal</a> einsehen.</p>
<p>Mit freundlichen Gruessen<br>
<strong>{EmailVorlagen.KANZLEI_NAME}</strong></p>
</body>
</html>
"""
        return EmailNachricht(
            empfaenger="",
            betreff=betreff,
            text_inhalt=text,
            html_inhalt=html
        )

    @staticmethod
    def dokument_hochgeladen(name: str, dokument_name: str, aktenzeichen: str) -> EmailNachricht:
        """Benachrichtigung ueber neues Dokument"""
        betreff = f"Neues Dokument in Akte {aktenzeichen}"

        text = f"""
Sehr geehrte(r) {name},

ein neues Dokument wurde zu Ihrer Akte hinzugefuegt.

Akte: {aktenzeichen}
Dokument: {dokument_name}

Sie koennen das Dokument in unserem Mandantenportal einsehen.

Mit freundlichen Gruessen
{EmailVorlagen.KANZLEI_NAME}
"""
        return EmailNachricht(
            empfaenger="",
            betreff=betreff,
            text_inhalt=text
        )

    @staticmethod
    def termin_erinnerung(name: str, termin_datum: str, termin_art: str, ort: str) -> EmailNachricht:
        """Terminerinnerung"""
        betreff = f"Terminerinnerung: {termin_art} am {termin_datum}"

        text = f"""
Sehr geehrte(r) {name},

wir moechten Sie an Ihren bevorstehenden Termin erinnern:

Datum: {termin_datum}
Art: {termin_art}
Ort: {ort}

Bitte erscheinen Sie puenktlich und bringen Sie alle relevanten Unterlagen mit.

Bei Verhinderung bitten wir um rechtzeitige Absage.

Mit freundlichen Gruessen
{EmailVorlagen.KANZLEI_NAME}
"""

        html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
<h2 style="color: #2c5282;">Terminerinnerung</h2>
<p>Sehr geehrte(r) {name},</p>
<p>wir moechten Sie an Ihren bevorstehenden Termin erinnern:</p>
<div style="background: #fefcbf; border-left: 4px solid #d69e2e; padding: 15px; margin: 20px 0;">
<p><strong>Datum:</strong> {termin_datum}</p>
<p><strong>Art:</strong> {termin_art}</p>
<p><strong>Ort:</strong> {ort}</p>
</div>
<p>Bitte erscheinen Sie puenktlich und bringen Sie alle relevanten Unterlagen mit.</p>
<p style="color: #c53030;"><em>Bei Verhinderung bitten wir um rechtzeitige Absage.</em></p>
<p>Mit freundlichen Gruessen<br>
<strong>{EmailVorlagen.KANZLEI_NAME}</strong></p>
</body>
</html>
"""
        return EmailNachricht(
            empfaenger="",
            betreff=betreff,
            text_inhalt=text,
            html_inhalt=html,
            prioritaet=EmailPrioritaet.HOCH
        )

    @staticmethod
    def frist_warnung(anwalt_name: str, aktenzeichen: str, frist_datum: str, frist_bezeichnung: str) -> EmailNachricht:
        """Fristwarnung fuer Anwaelte"""
        betreff = f"FRISTWARNUNG: {frist_bezeichnung} - {aktenzeichen}"

        text = f"""
ACHTUNG - FRISTWARNUNG

{anwalt_name},

folgende Frist laeuft in Kuerze ab:

Akte: {aktenzeichen}
Frist: {frist_bezeichnung}
Ablaufdatum: {frist_datum}

Bitte pruefen Sie die Akte und ergreifen Sie rechtzeitig Massnahmen.

Diese E-Mail wurde automatisch generiert.
FamilyKom - {EmailVorlagen.KANZLEI_NAME}
"""

        html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
<div style="background: #fed7d7; border: 2px solid #c53030; padding: 20px; border-radius: 8px;">
<h2 style="color: #c53030; margin-top: 0;">FRISTWARNUNG</h2>
<p>{anwalt_name},</p>
<p>folgende Frist laeuft in Kuerze ab:</p>
<div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
<p><strong>Akte:</strong> {aktenzeichen}</p>
<p><strong>Frist:</strong> {frist_bezeichnung}</p>
<p style="font-size: 1.2em; color: #c53030;"><strong>Ablaufdatum: {frist_datum}</strong></p>
</div>
<p><strong>Bitte pruefen Sie die Akte und ergreifen Sie rechtzeitig Massnahmen.</strong></p>
</div>
<p style="color: #718096; font-size: 0.9em; margin-top: 20px;">Diese E-Mail wurde automatisch generiert.<br>
FamilyKom - {EmailVorlagen.KANZLEI_NAME}</p>
</body>
</html>
"""
        return EmailNachricht(
            empfaenger="",
            betreff=betreff,
            text_inhalt=text,
            html_inhalt=html,
            prioritaet=EmailPrioritaet.HOCH
        )

    @staticmethod
    def mandanten_einladung(anwalt_name: str, mandant_name: str, zugangscode: str) -> EmailNachricht:
        """Einladung fuer Mandanten zum Portal"""
        betreff = f"Einladung zum Mandantenportal - {EmailVorlagen.KANZLEI_NAME}"

        text = f"""
Sehr geehrte(r) {mandant_name},

{anwalt_name} von {EmailVorlagen.KANZLEI_NAME} laedt Sie zu unserem Mandantenportal ein.

Mit diesem Portal koennen Sie:
- Ihre Akten und Dokumente einsehen
- Neue Dokumente hochladen
- Mit Ihrem Anwalt kommunizieren
- Termine und Fristen verfolgen

Ihr Zugangscode: {zugangscode}

Registrieren Sie sich unter:
https://familykom.rhm-rendsburg.de/register

Mit freundlichen Gruessen
{EmailVorlagen.KANZLEI_NAME}
"""

        html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
<h2 style="color: #2c5282;">Einladung zum Mandantenportal</h2>
<p>Sehr geehrte(r) {mandant_name},</p>
<p><strong>{anwalt_name}</strong> von {EmailVorlagen.KANZLEI_NAME} laedt Sie zu unserem Mandantenportal ein.</p>
<p>Mit diesem Portal koennen Sie:</p>
<ul>
<li>Ihre Akten und Dokumente einsehen</li>
<li>Neue Dokumente hochladen</li>
<li>Mit Ihrem Anwalt kommunizieren</li>
<li>Termine und Fristen verfolgen</li>
</ul>
<div style="background: #c6f6d5; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
<p style="margin: 0; font-size: 0.9em;">Ihr Zugangscode:</p>
<p style="font-size: 1.5em; font-weight: bold; letter-spacing: 3px; margin: 10px 0;">{zugangscode}</p>
</div>
<p style="text-align: center;">
<a href="https://familykom.rhm-rendsburg.de/register" style="background: #2c5282; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Jetzt registrieren</a>
</p>
<p>Mit freundlichen Gruessen<br>
<strong>{EmailVorlagen.KANZLEI_NAME}</strong></p>
</body>
</html>
"""
        return EmailNachricht(
            empfaenger="",
            betreff=betreff,
            text_inhalt=text,
            html_inhalt=html
        )


class EmailService:
    """
    E-Mail Service fuer FamilyKom

    Unterstuetzt:
    - SMTP (Standard E-Mail Server)
    - Resend API (empfohlen fuer Produktion)
    - Demo-Modus (E-Mails werden nur geloggt)
    """

    def __init__(
        self,
        demo_modus: bool = True,
        smtp_host: str = None,
        smtp_port: int = 587,
        smtp_benutzer: str = None,
        smtp_passwort: str = None,
        smtp_tls: bool = True,
        resend_api_key: str = None,
        absender_email: str = "noreply@rhm-rendsburg.de",
        absender_name: str = "FamilyKom"
    ):
        """
        Initialisiert den E-Mail Service

        Args:
            demo_modus: Wenn True, werden E-Mails nur simuliert
            smtp_host: SMTP Server Hostname
            smtp_port: SMTP Server Port (default 587)
            smtp_benutzer: SMTP Benutzername
            smtp_passwort: SMTP Passwort
            smtp_tls: TLS verwenden (default True)
            resend_api_key: API Key fuer Resend
            absender_email: Standard-Absender E-Mail
            absender_name: Standard-Absender Name
        """
        self.demo_modus = demo_modus
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST')
        self.smtp_port = smtp_port
        self.smtp_benutzer = smtp_benutzer or os.getenv('SMTP_USER')
        self.smtp_passwort = smtp_passwort or os.getenv('SMTP_PASSWORD')
        self.smtp_tls = smtp_tls
        self.resend_api_key = resend_api_key or os.getenv('RESEND_API_KEY')
        self.absender_email = absender_email
        self.absender_name = absender_name

        # Gesendete E-Mails Log (fuer Demo-Modus)
        self.email_log: List[Dict] = []

    def ist_konfiguriert(self) -> tuple[bool, str]:
        """
        Prueft ob der E-Mail Service konfiguriert ist

        Returns:
            Tuple aus (konfiguriert, meldung)
        """
        if self.demo_modus:
            return True, "E-Mail Service laeuft im Demo-Modus"

        if self.resend_api_key:
            if RESEND_VERFUEGBAR:
                return True, "E-Mail Service verwendet Resend API"
            else:
                return False, "Resend API Key konfiguriert aber resend-Paket nicht installiert"

        if self.smtp_host and self.smtp_benutzer and self.smtp_passwort:
            return True, "E-Mail Service verwendet SMTP"

        return False, "E-Mail Service nicht konfiguriert. SMTP oder Resend erforderlich."

    def sende_email(self, nachricht: EmailNachricht, empfaenger: str = None) -> EmailErgebnis:
        """
        Sendet eine E-Mail

        Args:
            nachricht: Die zu sendende Nachricht
            empfaenger: Optionaler Empfaenger (ueberschreibt nachricht.empfaenger)

        Returns:
            EmailErgebnis
        """
        ziel = empfaenger or nachricht.empfaenger

        if self.demo_modus:
            return self._demo_senden(nachricht, ziel)

        if self.resend_api_key and RESEND_VERFUEGBAR:
            return self._sende_via_resend(nachricht, ziel)

        if self.smtp_host:
            return self._sende_via_smtp(nachricht, ziel)

        return EmailErgebnis(
            erfolg=False,
            empfaenger=ziel,
            fehler="E-Mail Service nicht konfiguriert"
        )

    def _demo_senden(self, nachricht: EmailNachricht, empfaenger: str) -> EmailErgebnis:
        """Simuliert E-Mail Versand im Demo-Modus"""
        import uuid

        message_id = f"demo-{uuid.uuid4().hex[:12]}"

        log_eintrag = {
            'message_id': message_id,
            'zeitstempel': datetime.now().isoformat(),
            'empfaenger': empfaenger,
            'betreff': nachricht.betreff,
            'prioritaet': nachricht.prioritaet.value,
            'hat_html': nachricht.html_inhalt is not None,
            'anhaenge': len(nachricht.anhaenge)
        }
        self.email_log.append(log_eintrag)

        print(f"[DEMO] E-Mail gesendet an {empfaenger}: {nachricht.betreff}")

        return EmailErgebnis(
            erfolg=True,
            message_id=message_id,
            empfaenger=empfaenger
        )

    def _sende_via_smtp(self, nachricht: EmailNachricht, empfaenger: str) -> EmailErgebnis:
        """Sendet E-Mail via SMTP"""
        try:
            # Nachricht erstellen
            if nachricht.html_inhalt:
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(nachricht.text_inhalt, 'plain', 'utf-8'))
                msg.attach(MIMEText(nachricht.html_inhalt, 'html', 'utf-8'))
            else:
                msg = MIMEMultipart()
                msg.attach(MIMEText(nachricht.text_inhalt, 'plain', 'utf-8'))

            msg['Subject'] = nachricht.betreff
            msg['From'] = f"{self.absender_name} <{self.absender_email}>"
            msg['To'] = empfaenger

            if nachricht.cc:
                msg['Cc'] = ', '.join(nachricht.cc)
            if nachricht.antwort_an:
                msg['Reply-To'] = nachricht.antwort_an

            # Prioritaet Header
            if nachricht.prioritaet == EmailPrioritaet.HOCH:
                msg['X-Priority'] = '1'
                msg['Importance'] = 'high'
            elif nachricht.prioritaet == EmailPrioritaet.NIEDRIG:
                msg['X-Priority'] = '5'
                msg['Importance'] = 'low'

            # Anhaenge hinzufuegen
            for anhang in nachricht.anhaenge:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(anhang.inhalt)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{anhang.dateiname}"'
                )
                msg.attach(part)

            # Alle Empfaenger sammeln
            alle_empfaenger = [empfaenger]
            if nachricht.cc:
                alle_empfaenger.extend(nachricht.cc)
            if nachricht.bcc:
                alle_empfaenger.extend(nachricht.bcc)

            # Senden
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                server.login(self.smtp_benutzer, self.smtp_passwort)
                server.sendmail(self.absender_email, alle_empfaenger, msg.as_string())

            return EmailErgebnis(
                erfolg=True,
                message_id=msg.get('Message-ID', 'smtp-' + datetime.now().strftime('%Y%m%d%H%M%S')),
                empfaenger=empfaenger
            )

        except Exception as e:
            return EmailErgebnis(
                erfolg=False,
                empfaenger=empfaenger,
                fehler=str(e)
            )

    def _sende_via_resend(self, nachricht: EmailNachricht, empfaenger: str) -> EmailErgebnis:
        """Sendet E-Mail via Resend API"""
        try:
            resend.api_key = self.resend_api_key

            params = {
                'from': f"{self.absender_name} <{self.absender_email}>",
                'to': [empfaenger],
                'subject': nachricht.betreff,
                'text': nachricht.text_inhalt
            }

            if nachricht.html_inhalt:
                params['html'] = nachricht.html_inhalt

            if nachricht.cc:
                params['cc'] = nachricht.cc
            if nachricht.bcc:
                params['bcc'] = nachricht.bcc
            if nachricht.antwort_an:
                params['reply_to'] = nachricht.antwort_an

            # Anhaenge
            if nachricht.anhaenge:
                params['attachments'] = [
                    {
                        'filename': a.dateiname,
                        'content': list(a.inhalt)
                    }
                    for a in nachricht.anhaenge
                ]

            email = resend.Emails.send(params)

            return EmailErgebnis(
                erfolg=True,
                message_id=email.get('id'),
                empfaenger=empfaenger
            )

        except Exception as e:
            return EmailErgebnis(
                erfolg=False,
                empfaenger=empfaenger,
                fehler=str(e)
            )

    # Komfort-Methoden fuer haeufige E-Mail-Typen

    def sende_willkommens_email(
        self,
        empfaenger: str,
        name: str,
        benutzername: str,
        temp_passwort: str = None
    ) -> EmailErgebnis:
        """Sendet Willkommens-E-Mail"""
        nachricht = EmailVorlagen.willkommen(name, benutzername, temp_passwort)
        return self.sende_email(nachricht, empfaenger)

    def sende_passwort_reset(
        self,
        empfaenger: str,
        name: str,
        reset_link: str
    ) -> EmailErgebnis:
        """Sendet Passwort-Reset E-Mail"""
        nachricht = EmailVorlagen.passwort_reset(name, reset_link)
        return self.sende_email(nachricht, empfaenger)

    def sende_neue_akte_benachrichtigung(
        self,
        empfaenger: str,
        mandant_name: str,
        aktenzeichen: str,
        anwalt_name: str
    ) -> EmailErgebnis:
        """Sendet Benachrichtigung ueber neue Akte"""
        nachricht = EmailVorlagen.neue_akte(mandant_name, aktenzeichen, anwalt_name)
        return self.sende_email(nachricht, empfaenger)

    def sende_termin_erinnerung(
        self,
        empfaenger: str,
        name: str,
        termin_datum: str,
        termin_art: str,
        ort: str
    ) -> EmailErgebnis:
        """Sendet Terminerinnerung"""
        nachricht = EmailVorlagen.termin_erinnerung(name, termin_datum, termin_art, ort)
        return self.sende_email(nachricht, empfaenger)

    def sende_frist_warnung(
        self,
        empfaenger: str,
        anwalt_name: str,
        aktenzeichen: str,
        frist_datum: str,
        frist_bezeichnung: str
    ) -> EmailErgebnis:
        """Sendet Fristwarnung"""
        nachricht = EmailVorlagen.frist_warnung(anwalt_name, aktenzeichen, frist_datum, frist_bezeichnung)
        return self.sende_email(nachricht, empfaenger)

    def sende_mandanten_einladung(
        self,
        empfaenger: str,
        anwalt_name: str,
        mandant_name: str,
        zugangscode: str
    ) -> EmailErgebnis:
        """Sendet Mandanten-Einladung"""
        nachricht = EmailVorlagen.mandanten_einladung(anwalt_name, mandant_name, zugangscode)
        return self.sende_email(nachricht, empfaenger)

    def hole_email_log(self) -> List[Dict]:
        """Gibt den E-Mail Log zurueck (nur im Demo-Modus relevant)"""
        return self.email_log.copy()


# Komfort-Funktionen

def erstelle_email_service(demo_modus: bool = True) -> EmailService:
    """
    Erstellt einen EmailService mit Umgebungsvariablen

    Args:
        demo_modus: Demo-Modus aktivieren

    Returns:
        Konfigurierter EmailService
    """
    return EmailService(
        demo_modus=demo_modus,
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_benutzer=os.getenv('SMTP_USER'),
        smtp_passwort=os.getenv('SMTP_PASSWORD'),
        resend_api_key=os.getenv('RESEND_API_KEY'),
        absender_email=os.getenv('EMAIL_FROM', 'noreply@rhm-rendsburg.de'),
        absender_name=os.getenv('EMAIL_FROM_NAME', 'FamilyKom')
    )
