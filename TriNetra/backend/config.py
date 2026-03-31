import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'trinetra-secret-key-2025'
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'transactions.db')
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5001

    # Supabase – set these in .env to enable Supabase; falls back to SQLite otherwise
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')