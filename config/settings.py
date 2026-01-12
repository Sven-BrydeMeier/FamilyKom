"""
Anwendungseinstellungen für FamilyKom
Lädt Konfiguration aus Umgebungsvariablen
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Zentrale Anwendungskonfiguration"""

    # Application
    app_name: str = "FamilyKom"
    app_version: str = "1.0.0"
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str = "change-me-in-production"

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: Optional[str] = None

    # Upstash Redis
    upstash_redis_url: str = ""
    upstash_redis_token: str = ""

    # OCR
    google_vision_api_key: Optional[str] = None
    tesseract_cmd: str = "/usr/bin/tesseract"

    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # Cache TTL (in seconds)
    cache_ttl_default: int = 3600  # 1 hour
    cache_ttl_tabelle: int = 86400  # 24 hours
    cache_ttl_session: int = 1800  # 30 minutes

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Gibt gecachte Settings-Instanz zurück"""
    return Settings()


settings = get_settings()
