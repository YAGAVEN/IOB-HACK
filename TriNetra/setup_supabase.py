#!/usr/bin/env python3
"""
TriNetra Supabase Setup & Seed Script
Requires: SUPABASE_URL and SUPABASE_KEY in .env
"""
import os, sys, time, random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

GREEN  = '\033[0;32m'
CYAN   = '\033[0;36m'
RED    = '\033[0;31m'
YELLOW = '\033[1;33m'
BOLD   = '\033[1m'
NC     = '\033[0m'

def step(msg):  print(f'{CYAN}→  {msg}{NC}')
def ok(msg):    print(f'{GREEN}✓  {msg}{NC}')
def warn(msg):  print(f'{YELLOW}⚠  {msg}{NC}')
def fail(msg):  print(f'{RED}✗  {msg}{NC}')
def info(msg):  print(f'   {msg}')

# Account type / risk metadata keyed by naming prefix
_PROFILE = {
    'TERROR_CELL':     ('individual',  'Pakistan',      'CRITICAL', (75, 100)),
    'DONOR':           ('individual',  'Saudi Arabia',  'HIGH',     (55, 85)),
    'HANDLER':         ('individual',  'Afghanistan',   'HIGH',     (60, 90)),
    'FRONT_BUSINESS':  ('business',    'UAE',           'HIGH',     (50, 80)),
    'EXCHANGE':        ('exchange',    'Russia',        'HIGH',     (55, 85)),
    'MIXER':           ('mixer',       'North Korea',   'CRITICAL', (80, 100)),
    'WALLET':          ('crypto',      'Anonymous',     'CRITICAL', (70, 95)),
    'SHELL':           ('business',    'Cayman Islands','HIGH',     (60, 88)),
}
_COUNTRIES = ['India', 'USA', 'UK', 'Germany', 'Singapore', 'Japan', 'Australia', 'Canada']

def _profile_account(account_id: str):
    prefix = '_'.join(account_id.split('_')[:-1]).upper()
    for key, (atype, country, risk, score_range) in _PROFILE.items():
        if prefix.startswith(key):
            return atype, country, risk, score_range
    return 'individual', random.choice(_COUNTRIES), 'LOW', (5, 40)

def _seed_accounts_and_risk(sb):
    """Populate accounts and account_risk_scores from existing transactions."""
    # Check accounts table
    try:
        res = sb.table('accounts').select('account_id', count='exact').execute()
        if (res.count or 0) > 0:
            ok(f"Accounts already populated ({res.count} rows)")
            _ensure_risk_scores(sb)
            return
    except Exception:
        pass

    step("Fetching all transactions to build account list…")
    try:
        res = sb.table('transactions').select('from_account,to_account,scenario').execute()
        rows = res.data or []
    except Exception as e:
        warn(f"Could not fetch transactions: {e}")
        return

    if not rows:
        warn("No transactions found — skipping account seeding")
        return

    # Collect unique accounts with their dominant scenario
    account_scenarios: dict[str, set] = {}
    for r in rows:
        for col in ('from_account', 'to_account'):
            acc = r.get(col, '')
            if acc:
                account_scenarios.setdefault(acc, set()).add(r.get('scenario', 'normal'))

    step(f"Seeding {len(account_scenarios)} accounts…")
    account_records = []
    risk_records = []
    now = datetime.now().isoformat()

    for acc_id, scenarios in account_scenarios.items():
        atype, country, risk_level, score_range = _profile_account(acc_id)
        # Boost risk level if appears in high-risk scenarios
        high_risk_scenarios = {'terrorist_financing', 'crypto_sanctions', 'human_trafficking'}
        if scenarios & high_risk_scenarios and risk_level == 'LOW':
            risk_level = 'MEDIUM'

        account_records.append({
            'account_id':   acc_id,
            'account_name': acc_id.replace('_', ' ').title(),
            'account_type': atype,
            'country':      country,
            'risk_level':   risk_level,
        })

        score = round(random.uniform(*score_range), 2)
        risk_records.append({
            'account_id':   acc_id,
            'risk_score':   score,
            'last_updated': now,
        })

    # Insert accounts
    CHUNK = 200
    inserted_acc = 0
    for i in range(0, len(account_records), CHUNK):
        try:
            sb.table('accounts').upsert(account_records[i:i+CHUNK]).execute()
            inserted_acc += len(account_records[i:i+CHUNK])
        except Exception as e:
            warn(f"Accounts chunk error: {e}")
    ok(f"Inserted {inserted_acc} accounts")

    # Insert risk scores
    inserted_risk = 0
    for i in range(0, len(risk_records), CHUNK):
        try:
            sb.table('account_risk_scores').upsert(risk_records[i:i+CHUNK]).execute()
            inserted_risk += len(risk_records[i:i+CHUNK])
        except Exception as e:
            warn(f"Risk scores chunk error: {e}")
    ok(f"Inserted {inserted_risk} account risk scores")

def _ensure_risk_scores(sb):
    """Add risk scores if missing."""
    try:
        res = sb.table('account_risk_scores').select('account_id', count='exact').execute()
        if (res.count or 0) > 0:
            ok(f"Risk scores already populated ({res.count} rows)")
            return
    except Exception:
        pass
    # Reuse same logic — fetch accounts and score them
    try:
        res = sb.table('accounts').select('account_id,risk_level').execute()
        rows = res.data or []
        if not rows:
            return
        now = datetime.now().isoformat()
        _SCORE_MAP = {'LOW': (5,40), 'MEDIUM': (30,60), 'HIGH': (55,85), 'CRITICAL': (70,100)}
        risk_records = []
        for r in rows:
            sr = _SCORE_MAP.get(r.get('risk_level','LOW'), (5,40))
            risk_records.append({'account_id': r['account_id'],
                                  'risk_score': round(random.uniform(*sr), 2),
                                  'last_updated': now})
        for i in range(0, len(risk_records), 200):
            sb.table('account_risk_scores').upsert(risk_records[i:i+200]).execute()
        ok(f"Inserted {len(risk_records)} risk scores")
    except Exception as e:
        warn(f"Risk score seeding failed: {e}")

# ── Validate env ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

if not SUPABASE_URL or not SUPABASE_KEY:
    fail("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

# ── Init Supabase REST client ─────────────────────────────────────────────────
step("Connecting to Supabase REST API…")
try:
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    ok(f"Connected: {SUPABASE_URL}")
except Exception as e:
    fail(f"Could not create Supabase client: {e}")
    sys.exit(1)

# ── Check if tables exist ─────────────────────────────────────────────────────
def tables_exist():
    try:
        sb.table('transactions').select('id', count='exact').limit(1).execute()
        return True
    except Exception as e:
        return False

step("Checking database tables…")
if not tables_exist():
    print()
    print(f"{YELLOW}{BOLD}Tables not found in Supabase.{NC}")
    print(f"Please run the following SQL in your Supabase SQL Editor:")
    print(f"  {CYAN}https://supabase.com/dashboard/project/aszzqexlltiwcpbkamcz/sql{NC}")
    print()

    SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'backend', 'database', 'schema.sql')
    with open(SCHEMA_FILE) as f:
        schema = f.read()

    print(f"{BOLD}{'─'*60}{NC}")
    print(schema)
    print(f"{BOLD}{'─'*60}{NC}")
    print()
    input(f"{YELLOW}  ↳ Paste the SQL above into Supabase → SQL Editor → Run, then press Enter here…{NC} ")
    print()

    step("Verifying tables were created…")
    for i in range(5):
        time.sleep(1)
        if tables_exist():
            ok("Tables found!")
            break
    else:
        fail("Tables still not found. Run the SQL and try again.")
        sys.exit(1)
else:
    ok("Tables exist")

# ── Check if data already seeded ─────────────────────────────────────────────
step("Checking existing data…")
try:
    res = sb.table('transactions').select('id', count='exact').execute()
    count = res.count or 0
except Exception:
    count = 0

if count > 0:
    ok(f"Already seeded ({count} transactions) — nothing to do.")
    # Still seed accounts/risk if missing
    _seed_accounts_and_risk(sb)
    print(f"\n{GREEN}🎉  Supabase is ready! Start TriNetra with ./start.sh{NC}\n")
    sys.exit(0)

ok("Database is empty — seeding synthetic data…")

# ── Generate synthetic data ───────────────────────────────────────────────────
step("Generating transactions…")
try:
    from config import Config
    from data.synthetic_generator import TriNetraDataGenerator

    gen = TriNetraDataGenerator(Config.DATABASE_PATH)
    all_tx = []
    for scenario in ['terrorist_financing', 'crypto_sanctions', 'human_trafficking']:
        all_tx.extend(gen.generate_scenario_data(scenario, 150))
    all_tx.extend(gen.generate_scenario_data('normal', 300))
    ok(f"Generated {len(all_tx)} transactions")
except Exception as e:
    fail(f"Data generation failed: {e}")
    sys.exit(1)

# ── Insert via REST (HTTP — works regardless of IPv6) ─────────────────────────
step("Inserting into Supabase via REST API…")
try:
    CHUNK = 200
    total = len(all_tx)
    inserted = 0
    for i in range(0, total, CHUNK):
        chunk = all_tx[i:i + CHUNK]
        sb.table('transactions').insert(chunk).execute()
        inserted += len(chunk)
        pct = int(inserted / total * 40)
        bar = '█' * pct + '░' * (40 - pct)
        print(f"\r  [{bar}] {inserted}/{total}", end='', flush=True)
    print()
    ok(f"✅  {inserted} transactions inserted!")
except Exception as e:
    fail(f"Insert failed: {e}")
    sys.exit(1)

# ── Seed accounts + risk scores ───────────────────────────────────────────────
_seed_accounts_and_risk(sb)

print(f"\n{GREEN}🎉  Supabase setup complete! Start TriNetra with ./start.sh{NC}\n")
