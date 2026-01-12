"""
Upstash Redis Cache für FamilyKom

Implementiert Caching-Strategien für:
- Session-Management
- Berechnungs-Cache
- OLG-Leitlinien
- Düsseldorfer Tabelle
- Rate-Limiting
"""

import json
from functools import lru_cache
from typing import Optional, Any, Dict
from datetime import timedelta

from upstash_redis import Redis

from config.settings import settings


@lru_cache()
def get_redis_client() -> Optional[Redis]:
    """
    Gibt eine gecachte Upstash Redis-Client-Instanz zurück

    Returns None wenn keine Konfiguration vorhanden ist.
    """
    if not settings.upstash_redis_url or not settings.upstash_redis_token:
        return None

    return Redis(
        url=settings.upstash_redis_url,
        token=settings.upstash_redis_token
    )


class CacheService:
    """
    Service für Redis-Caching-Operationen

    Bietet typsichere Methoden für häufige Caching-Szenarien.
    """

    # Cache-Key-Präfixe
    PREFIX_SESSION = "session:"
    PREFIX_CALCULATION = "calc:"
    PREFIX_TABELLE = "tabelle:"
    PREFIX_OLG = "olg:"
    PREFIX_RATE_LIMIT = "rate:"
    PREFIX_USER = "user:"

    def __init__(self, client: Redis = None):
        self.client = client or get_redis_client()
        self._enabled = self.client is not None

    @property
    def is_enabled(self) -> bool:
        """Prüft ob Redis verfügbar ist"""
        return self._enabled

    def _serialize(self, value: Any) -> str:
        """Serialisiert einen Wert für Redis"""
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        return str(value)

    def _deserialize(self, value: str, as_json: bool = False) -> Any:
        """Deserialisiert einen Redis-Wert"""
        if value is None:
            return None
        if as_json:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    # =========================================================================
    # Basis-Operationen
    # =========================================================================

    def get(self, key: str, as_json: bool = False) -> Optional[Any]:
        """Holt einen Wert aus dem Cache"""
        if not self._enabled:
            return None

        value = self.client.get(key)
        return self._deserialize(value, as_json)

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = None
    ) -> bool:
        """Setzt einen Wert im Cache"""
        if not self._enabled:
            return False

        serialized = self._serialize(value)

        if ttl_seconds:
            self.client.setex(key, ttl_seconds, serialized)
        else:
            self.client.set(key, serialized)

        return True

    def delete(self, key: str) -> bool:
        """Löscht einen Wert aus dem Cache"""
        if not self._enabled:
            return False

        self.client.delete(key)
        return True

    def exists(self, key: str) -> bool:
        """Prüft ob ein Key existiert"""
        if not self._enabled:
            return False

        return self.client.exists(key) > 0

    def ttl(self, key: str) -> Optional[int]:
        """Gibt die verbleibende TTL eines Keys zurück"""
        if not self._enabled:
            return None

        return self.client.ttl(key)

    # =========================================================================
    # Session-Management
    # =========================================================================

    def set_session(
        self,
        session_id: str,
        user_data: Dict,
        ttl_seconds: int = None
    ) -> bool:
        """Speichert Session-Daten"""
        ttl = ttl_seconds or settings.cache_ttl_session
        key = f"{self.PREFIX_SESSION}{session_id}"
        return self.set(key, user_data, ttl)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Holt Session-Daten"""
        key = f"{self.PREFIX_SESSION}{session_id}"
        return self.get(key, as_json=True)

    def delete_session(self, session_id: str) -> bool:
        """Löscht eine Session"""
        key = f"{self.PREFIX_SESSION}{session_id}"
        return self.delete(key)

    def refresh_session(self, session_id: str, ttl_seconds: int = None) -> bool:
        """Verlängert die Session-TTL"""
        if not self._enabled:
            return False

        ttl = ttl_seconds or settings.cache_ttl_session
        key = f"{self.PREFIX_SESSION}{session_id}"

        if self.exists(key):
            self.client.expire(key, ttl)
            return True
        return False

    # =========================================================================
    # Berechnungs-Cache
    # =========================================================================

    def cache_calculation(
        self,
        case_id: str,
        calc_type: str,
        calc_hash: str,
        result: Dict,
        ttl_seconds: int = None
    ) -> bool:
        """Cacht eine Berechnung"""
        ttl = ttl_seconds or settings.cache_ttl_default
        key = f"{self.PREFIX_CALCULATION}{case_id}:{calc_type}:{calc_hash}"
        return self.set(key, result, ttl)

    def get_cached_calculation(
        self,
        case_id: str,
        calc_type: str,
        calc_hash: str
    ) -> Optional[Dict]:
        """Holt eine gecachte Berechnung"""
        key = f"{self.PREFIX_CALCULATION}{case_id}:{calc_type}:{calc_hash}"
        return self.get(key, as_json=True)

    def invalidate_case_calculations(self, case_id: str) -> bool:
        """Invalidiert alle Berechnungen einer Akte"""
        if not self._enabled:
            return False

        # Pattern-basiertes Löschen
        pattern = f"{self.PREFIX_CALCULATION}{case_id}:*"
        keys = self.client.keys(pattern)

        if keys:
            for key in keys:
                self.client.delete(key)

        return True

    # =========================================================================
    # Düsseldorfer Tabelle Cache
    # =========================================================================

    def cache_tabelle(
        self,
        jahr: int,
        tabelle_data: Dict,
        ttl_seconds: int = None
    ) -> bool:
        """Cacht die Düsseldorfer Tabelle"""
        ttl = ttl_seconds or settings.cache_ttl_tabelle
        key = f"{self.PREFIX_TABELLE}{jahr}"
        return self.set(key, tabelle_data, ttl)

    def get_cached_tabelle(self, jahr: int) -> Optional[Dict]:
        """Holt die gecachte Düsseldorfer Tabelle"""
        key = f"{self.PREFIX_TABELLE}{jahr}"
        return self.get(key, as_json=True)

    # =========================================================================
    # OLG-Leitlinien Cache
    # =========================================================================

    def cache_olg_leitlinien(
        self,
        olg_bezirk: str,
        jahr: int,
        leitlinien_data: Dict,
        ttl_seconds: int = None
    ) -> bool:
        """Cacht OLG-Leitlinien"""
        ttl = ttl_seconds or settings.cache_ttl_tabelle
        key = f"{self.PREFIX_OLG}{olg_bezirk}:{jahr}"
        return self.set(key, leitlinien_data, ttl)

    def get_cached_olg_leitlinien(
        self,
        olg_bezirk: str,
        jahr: int
    ) -> Optional[Dict]:
        """Holt gecachte OLG-Leitlinien"""
        key = f"{self.PREFIX_OLG}{olg_bezirk}:{jahr}"
        return self.get(key, as_json=True)

    # =========================================================================
    # Rate Limiting
    # =========================================================================

    def check_rate_limit(
        self,
        identifier: str,
        action: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Prüft und aktualisiert Rate-Limit

        Args:
            identifier: Benutzer-ID oder IP
            action: Art der Aktion (z.B. 'login', 'api')
            max_requests: Maximale Anfragen im Zeitfenster
            window_seconds: Größe des Zeitfensters

        Returns:
            Tuple aus (erlaubt, verbleibende_anfragen)
        """
        if not self._enabled:
            return True, max_requests

        key = f"{self.PREFIX_RATE_LIMIT}{action}:{identifier}"

        current = self.client.get(key)

        if current is None:
            self.client.setex(key, window_seconds, 1)
            return True, max_requests - 1

        count = int(current)

        if count >= max_requests:
            return False, 0

        self.client.incr(key)
        return True, max_requests - count - 1

    def reset_rate_limit(self, identifier: str, action: str) -> bool:
        """Setzt ein Rate-Limit zurück"""
        key = f"{self.PREFIX_RATE_LIMIT}{action}:{identifier}"
        return self.delete(key)

    # =========================================================================
    # User Cache
    # =========================================================================

    def cache_user(
        self,
        user_id: str,
        user_data: Dict,
        ttl_seconds: int = None
    ) -> bool:
        """Cacht Benutzerdaten"""
        ttl = ttl_seconds or settings.cache_ttl_default
        key = f"{self.PREFIX_USER}{user_id}"
        return self.set(key, user_data, ttl)

    def get_cached_user(self, user_id: str) -> Optional[Dict]:
        """Holt gecachte Benutzerdaten"""
        key = f"{self.PREFIX_USER}{user_id}"
        return self.get(key, as_json=True)

    def invalidate_user(self, user_id: str) -> bool:
        """Invalidiert Benutzer-Cache"""
        key = f"{self.PREFIX_USER}{user_id}"
        return self.delete(key)

    # =========================================================================
    # Utility
    # =========================================================================

    def flush_all(self) -> bool:
        """
        Löscht den gesamten Cache

        ACHTUNG: Nur in Entwicklung verwenden!
        """
        if not self._enabled:
            return False

        if settings.app_env == "production":
            raise RuntimeError("flush_all ist in Produktion nicht erlaubt")

        self.client.flushdb()
        return True

    def health_check(self) -> Dict:
        """Prüft die Redis-Verbindung"""
        if not self._enabled:
            return {"status": "disabled", "message": "Redis nicht konfiguriert"}

        try:
            self.client.ping()
            return {"status": "ok", "message": "Redis-Verbindung erfolgreich"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
