"""
Supabase Client für FamilyKom

Stellt Verbindung zur Supabase-Datenbank her und bietet
Hilfsfunktionen für CRUD-Operationen.
"""

from functools import lru_cache
from typing import Optional, Dict, Any, List

from supabase import create_client, Client

from config.settings import settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Gibt eine gecachte Supabase-Client-Instanz zurück

    Verwendet den Anon-Key für normale Operationen.
    Für Admin-Operationen muss der Service-Key verwendet werden.
    """
    if not settings.supabase_url or not settings.supabase_key:
        raise ValueError(
            "Supabase-Konfiguration fehlt. "
            "Bitte SUPABASE_URL und SUPABASE_KEY in .env setzen."
        )

    return create_client(settings.supabase_url, settings.supabase_key)


def get_supabase_admin_client() -> Optional[Client]:
    """
    Gibt einen Supabase-Client mit Service-Key zurück

    Nur für Admin-Operationen verwenden (z.B. User-Management).
    """
    if not settings.supabase_url or not settings.supabase_service_key:
        return None

    return create_client(settings.supabase_url, settings.supabase_service_key)


class SupabaseRepository:
    """
    Basis-Repository für Supabase-Operationen

    Bietet CRUD-Methoden für alle Tabellen.
    """

    def __init__(self, table_name: str, client: Client = None):
        self.table_name = table_name
        self.client = client or get_supabase_client()

    def get_all(
        self,
        select: str = "*",
        filters: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None
    ) -> List[Dict]:
        """
        Holt alle Einträge einer Tabelle

        Args:
            select: Spalten zum Abrufen (default: alle)
            filters: Dictionary mit Filterkriterien
            order_by: Spalte für Sortierung
            limit: Maximale Anzahl Ergebnisse

        Returns:
            Liste von Dictionaries mit den Ergebnissen
        """
        query = self.client.table(self.table_name).select(select)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        if order_by:
            query = query.order(order_by)

        if limit:
            query = query.limit(limit)

        response = query.execute()
        return response.data

    def get_by_id(self, id: str, select: str = "*") -> Optional[Dict]:
        """Holt einen Eintrag nach ID"""
        response = (
            self.client.table(self.table_name)
            .select(select)
            .eq("id", id)
            .single()
            .execute()
        )
        return response.data

    def create(self, data: Dict[str, Any]) -> Dict:
        """Erstellt einen neuen Eintrag"""
        response = (
            self.client.table(self.table_name)
            .insert(data)
            .execute()
        )
        return response.data[0] if response.data else None

    def update(self, id: str, data: Dict[str, Any]) -> Dict:
        """Aktualisiert einen Eintrag"""
        response = (
            self.client.table(self.table_name)
            .update(data)
            .eq("id", id)
            .execute()
        )
        return response.data[0] if response.data else None

    def delete(self, id: str) -> bool:
        """Löscht einen Eintrag"""
        response = (
            self.client.table(self.table_name)
            .delete()
            .eq("id", id)
            .execute()
        )
        return len(response.data) > 0

    def upsert(self, data: Dict[str, Any], on_conflict: str = "id") -> Dict:
        """Erstellt oder aktualisiert einen Eintrag"""
        response = (
            self.client.table(self.table_name)
            .upsert(data, on_conflict=on_conflict)
            .execute()
        )
        return response.data[0] if response.data else None


# =============================================================================
# Spezialisierte Repositories
# =============================================================================

class UserRepository(SupabaseRepository):
    """Repository für Benutzer-Operationen"""

    def __init__(self, client: Client = None):
        super().__init__("users", client)

    def get_by_email(self, email: str) -> Optional[Dict]:
        """Sucht Benutzer nach E-Mail"""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )
        return response.data

    def get_by_auth_id(self, auth_id: str) -> Optional[Dict]:
        """Sucht Benutzer nach Auth-ID"""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("auth_id", auth_id)
            .single()
            .execute()
        )
        return response.data

    def get_lawyers(self) -> List[Dict]:
        """Holt alle Anwälte"""
        return self.get_all(
            filters={"role": "anwalt", "is_active": True},
            order_by="nachname"
        )


class ClientRepository(SupabaseRepository):
    """Repository für Mandanten-Operationen"""

    def __init__(self, client: Client = None):
        super().__init__("clients", client)

    def get_by_user_id(self, user_id: str) -> Optional[Dict]:
        """Holt Mandant zu einem User"""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return response.data

    def search(self, query: str) -> List[Dict]:
        """Sucht Mandanten nach Name"""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .or_(f"vorname.ilike.%{query}%,nachname.ilike.%{query}%")
            .execute()
        )
        return response.data


class CaseRepository(SupabaseRepository):
    """Repository für Akten-Operationen"""

    def __init__(self, client: Client = None):
        super().__init__("cases", client)

    def get_by_case_number(self, case_number: str) -> Optional[Dict]:
        """Holt Akte nach Aktenzeichen"""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("case_number", case_number)
            .single()
            .execute()
        )
        return response.data

    def get_by_access_code(self, access_code: str) -> Optional[Dict]:
        """Holt Akte nach Zugangscode"""
        response = (
            self.client.table(self.table_name)
            .select("*, clients(*), opponents(*)")
            .eq("access_code", access_code)
            .single()
            .execute()
        )
        return response.data

    def get_by_lawyer(self, lawyer_id: str, status: str = None) -> List[Dict]:
        """Holt alle Akten eines Anwalts"""
        query = (
            self.client.table(self.table_name)
            .select("*, clients(vorname, nachname), opponents(vorname, nachname)")
            .eq("lawyer_id", lawyer_id)
        )

        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True)
        response = query.execute()
        return response.data

    def get_by_client(self, client_id: str) -> List[Dict]:
        """Holt alle Akten eines Mandanten"""
        response = (
            self.client.table(self.table_name)
            .select("*, users!cases_lawyer_id_fkey(vorname, nachname)")
            .eq("client_id", client_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data


class DocumentRepository(SupabaseRepository):
    """Repository für Dokument-Operationen"""

    def __init__(self, client: Client = None):
        super().__init__("documents", client)

    def get_by_case(
        self,
        case_id: str,
        document_type: str = None,
        mandant_sichtbar: bool = None
    ) -> List[Dict]:
        """Holt alle Dokumente einer Akte"""
        query = (
            self.client.table(self.table_name)
            .select("*")
            .eq("case_id", case_id)
        )

        if document_type:
            query = query.eq("document_type", document_type)

        if mandant_sichtbar is not None:
            query = query.eq("mandant_sichtbar", mandant_sichtbar)

        query = query.order("created_at", desc=True)
        response = query.execute()
        return response.data

    def get_pending_ocr(self) -> List[Dict]:
        """Holt Dokumente die noch nicht per OCR verarbeitet wurden"""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("ocr_verarbeitet", False)
            .in_("dateityp", ["application/pdf", "image/jpeg", "image/png", "image/tiff"])
            .limit(50)
            .execute()
        )
        return response.data


class CalculationRepository(SupabaseRepository):
    """Repository für Berechnungs-Operationen"""

    def __init__(self, client: Client = None):
        super().__init__("calculations", client)

    def get_by_case(
        self,
        case_id: str,
        berechnungsart: str = None
    ) -> List[Dict]:
        """Holt alle Berechnungen einer Akte"""
        query = (
            self.client.table(self.table_name)
            .select("*, users(vorname, nachname)")
            .eq("case_id", case_id)
        )

        if berechnungsart:
            query = query.eq("berechnungsart", berechnungsart)

        query = query.order("created_at", desc=True)
        response = query.execute()
        return response.data

    def get_latest(
        self,
        case_id: str,
        berechnungsart: str
    ) -> Optional[Dict]:
        """Holt die neueste Berechnung einer Art"""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("case_id", case_id)
            .eq("berechnungsart", berechnungsart)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None


class IncomeRecordRepository(SupabaseRepository):
    """Repository für Einkommens-Operationen"""

    def __init__(self, client: Client = None):
        super().__init__("income_records", client)

    def get_by_case(
        self,
        case_id: str,
        person: str = None,
        jahr: int = None
    ) -> List[Dict]:
        """Holt alle Einkommenseinträge einer Akte"""
        query = (
            self.client.table(self.table_name)
            .select("*, documents(titel, dateiname)")
            .eq("case_id", case_id)
        )

        if person:
            query = query.eq("person", person)

        if jahr:
            query = query.eq("jahr", jahr)

        query = query.order("jahr", desc=True).order("monat", desc=True)
        response = query.execute()
        return response.data

    def get_average_income(
        self,
        case_id: str,
        person: str,
        monate: int = 12
    ) -> Optional[Dict]:
        """Berechnet das Durchschnittseinkommen"""
        records = self.get_by_case(case_id, person)[:monate]

        if not records:
            return None

        brutto_sum = sum(r.get("brutto_gesamt", 0) or 0 for r in records)
        netto_sum = sum(r.get("netto_gesamt", 0) or 0 for r in records)

        return {
            "monate": len(records),
            "brutto_durchschnitt": brutto_sum / len(records),
            "netto_durchschnitt": netto_sum / len(records),
        }
