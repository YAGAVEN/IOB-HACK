"""
Database utility layer for TriNetra.
Provides transparent SQLite ↔ Supabase switching via helper functions.
When SUPABASE_URL / SUPABASE_KEY are set in the environment, Supabase is used;
otherwise falls back to the local SQLite file.
"""
import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_config():
    from config import Config
    return Config


def _supabase():
    """Return Supabase client or None."""
    from database.supabase_client import get_supabase
    return get_supabase()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_df(table: str, filters: dict | None = None,
             columns: str = '*', order_by: str | None = None,
             limit: int | None = None) -> pd.DataFrame:
    """
    Fetch rows from *table* and return a pandas DataFrame.

    Parameters
    ----------
    table   : table name ('transactions', 'accounts', …)
    filters : dict of {column: value} for equality filters
    columns : comma-separated column list or '*'
    order_by: column name to order by (ascending)
    limit   : max rows to return
    """
    sb = _supabase()
    if sb is not None:
        return _supabase_fetch(sb, table, filters, columns, order_by, limit)
    return _sqlite_fetch(table, filters, columns, order_by, limit)


def fetch_transactions_since(start_date: datetime,
                              scenario: str | None = None) -> pd.DataFrame:
    """Convenience: fetch transactions since *start_date*, optionally filtered by scenario."""
    sb = _supabase()
    if sb is not None:
        q = sb.table('transactions').select('*').gte('timestamp', start_date.isoformat())
        if scenario and scenario != 'all':
            q = q.eq('scenario', scenario)
        res = q.order('timestamp').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    # SQLite fallback
    cfg = _get_config()
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    if scenario and scenario != 'all':
        df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE scenario = ? AND timestamp >= ? ORDER BY timestamp",
            conn, params=[scenario, start_date.isoformat()])
    else:
        df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE timestamp >= ? ORDER BY timestamp",
            conn, params=[start_date.isoformat()])
    conn.close()
    return df


def fetch_account_transactions(account_id: str) -> pd.DataFrame:
    """Fetch all transactions where account is sender or receiver."""
    sb = _supabase()
    if sb is not None:
        # PostgREST OR filter
        res = sb.table('transactions').select('*').or_(
            f'from_account.eq.{account_id},to_account.eq.{account_id}'
        ).order('timestamp').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    cfg = _get_config()
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE from_account = ? OR to_account = ? ORDER BY timestamp",
        conn, params=[account_id, account_id])
    conn.close()
    return df


def fetch_all_transactions() -> pd.DataFrame:
    """Fetch every transaction row."""
    sb = _supabase()
    if sb is not None:
        res = sb.table('transactions').select('*').order('timestamp').execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    cfg = _get_config()
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp", conn)
    conn.close()
    return df


def search_transactions(term: str, search_type: str = 'all') -> pd.DataFrame:
    """Search transactions by various criteria."""
    sb = _supabase()
    if sb is not None:
        if search_type == 'amount':
            try:
                res = sb.table('transactions').select('*').eq('amount', float(term)).execute()
            except ValueError:
                return pd.DataFrame()
        elif search_type == 'account':
            res = sb.table('transactions').select('*').or_(
                f'from_account.ilike.%{term}%,to_account.ilike.%{term}%'
            ).execute()
        elif search_type == 'id':
            res = sb.table('transactions').select('*').ilike('transaction_id', f'%{term}%').execute()
        else:
            res = sb.table('transactions').select('*').or_(
                f'transaction_id.ilike.%{term}%,from_account.ilike.%{term}%,to_account.ilike.%{term}%'
            ).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()

    # SQLite fallback
    cfg = _get_config()
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    if search_type == 'amount':
        df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE amount = ? ORDER BY timestamp DESC",
            conn, params=[float(term)])
    elif search_type == 'account':
        df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE from_account LIKE ? OR to_account LIKE ? ORDER BY timestamp DESC",
            conn, params=[f'%{term}%', f'%{term}%'])
    elif search_type == 'id':
        df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE transaction_id LIKE ? ORDER BY timestamp DESC",
            conn, params=[f'%{term}%'])
    else:
        pattern = f'%{term}%'
        df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE transaction_id LIKE ? OR from_account LIKE ? "
            "OR to_account LIKE ? OR CAST(amount AS TEXT) LIKE ? ORDER BY timestamp DESC",
            conn, params=[pattern, pattern, pattern, pattern])
    conn.close()
    return df


def upsert_risk_score(account_id: str, risk_score: float) -> None:
    """Insert or update an account risk score."""
    sb = _supabase()
    now = datetime.now().isoformat()
    if sb is not None:
        sb.table('account_risk_scores').upsert({
            'account_id': account_id,
            'risk_score': risk_score,
            'last_updated': now
        }).execute()
        return
    cfg = _get_config()
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO account_risk_scores (account_id, risk_score, last_updated) VALUES (?, ?, ?)",
        (account_id, risk_score, now))
    conn.commit()
    conn.close()


def get_risk_score(account_id: str) -> float | None:
    """Return stored risk score for an account, or None."""
    sb = _supabase()
    if sb is not None:
        res = sb.table('account_risk_scores').select('risk_score').eq('account_id', account_id).execute()
        if res.data:
            return res.data[0]['risk_score']
        return None
    cfg = _get_config()
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT risk_score FROM account_risk_scores WHERE account_id = ?", (account_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def count_transactions() -> int:
    """Count total transactions (used for init check)."""
    sb = _supabase()
    if sb is not None:
        res = sb.table('transactions').select('id', count='exact').execute()
        return res.count or 0
    cfg = _get_config()
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def bulk_insert_transactions(records: list[dict]) -> None:
    """Insert a list of transaction dicts."""
    if not records:
        return
    sb = _supabase()
    if sb is not None:
        # Supabase batch insert (chunked to avoid request size limits)
        chunk_size = 500
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            sb.table('transactions').insert(chunk).execute()
        return
    # SQLite fallback: use pandas
    cfg = _get_config()
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    df = pd.DataFrame(records)
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    conn.close()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _supabase_fetch(sb, table, filters, columns, order_by, limit):
    q = sb.table(table).select(columns)
    if filters:
        for col, val in filters.items():
            q = q.eq(col, val)
    if order_by:
        q = q.order(order_by)
    if limit:
        q = q.limit(limit)
    res = q.execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()


def _sqlite_fetch(table, filters, columns, order_by, limit):
    cfg = _get_config()
    col_str = columns if columns != '*' else '*'
    where_parts, params = [], []
    if filters:
        for col, val in filters.items():
            where_parts.append(f"{col} = ?")
            params.append(val)
    query = f"SELECT {col_str} FROM {table}"
    if where_parts:
        query += " WHERE " + " AND ".join(where_parts)
    if order_by:
        query += f" ORDER BY {order_by}"
    if limit:
        query += f" LIMIT {limit}"
    conn = sqlite3.connect(cfg.DATABASE_PATH)
    df = pd.read_sql_query(query, conn, params=params if params else None)
    conn.close()
    return df
