"""
Supabase client singleton for TriNetra backend.
Falls back to SQLite mode when SUPABASE_URL/SUPABASE_KEY are not set.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Ensure .env is loaded regardless of import order
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(_env_path)
except ImportError:
    pass

_supabase_client = None
_supabase_available = False


def get_supabase():
    """
    Return the Supabase client, or None if not configured.
    Initialised once and cached.
    """
    global _supabase_client, _supabase_available

    if _supabase_client is not None:
        return _supabase_client

    url = os.environ.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_KEY', '')

    if not url or not key:
        return None

    try:
        from supabase import create_client, Client
        _supabase_client = create_client(url, key)
        _supabase_available = True
        print("✅ Supabase client initialised")
        return _supabase_client
    except ImportError:
        print("⚠️  supabase-py not installed – falling back to SQLite")
        return None
    except Exception as e:
        print(f"⚠️  Supabase connection failed: {e} – falling back to SQLite")
        return None


def is_supabase_enabled() -> bool:
    """Return True if Supabase is configured and available."""
    return get_supabase() is not None
