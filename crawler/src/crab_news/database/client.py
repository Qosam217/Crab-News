"""Supabase client factory and manager."""

from typing import Optional
from supabase import create_client, Client
from ..config import settings
from ..utils.logger import logger

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Returns a singleton Supabase client instance configured with service_role key."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    if not settings.supabase_url or not settings.supabase_service_role_key:
        logger.warning(
            "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is not set. "
            "Database operations will fail unless dry-run is used."
        )
        # Placeholder client creation if needed in tests/dry-run
        return create_client(
            settings.supabase_url or "https://placeholder.supabase.co",
            settings.supabase_service_role_key or "placeholder-key",
        )

    _supabase_client = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
    return _supabase_client
