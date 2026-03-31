#!/bin/bash

echo "🔄 Regenerating TriNetra database with fresh timestamps..."

cd /media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/backend

# Activate virtual environment
source venv/bin/activate

# Run Python script to regenerate database
python3 << 'PYTHON_SCRIPT'
import sys
import os
from data.synthetic_generator import init_database
from config import Config

# Force regeneration by removing existing data
import sqlite3
conn = sqlite3.connect(Config.DATABASE_PATH)
cursor = conn.cursor()
cursor.execute("DELETE FROM transactions")
conn.commit()
conn.close()

print("🔄 Deleted old transactions, generating fresh data...")
init_database()

# Verify
from datetime import datetime, timedelta
conn = sqlite3.connect(Config.DATABASE_PATH)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM transactions')
total = cursor.fetchone()[0]

cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM transactions')
min_ts, max_ts = cursor.fetchone()

print(f"\n📊 Database Statistics:")
print(f"   Total transactions: {total}")
print(f"   Date range: {min_ts} to {max_ts}")

# Check last 30 days
thirty_days_ago = datetime.now() - timedelta(days=30)
cursor.execute('SELECT COUNT(*) FROM transactions WHERE timestamp >= ?', (thirty_days_ago.isoformat(),))
recent= cursor.fetchone()[0]
print(f"   Transactions (last 30 days): {recent}")

conn.close()
PYTHON_SCRIPT

echo "✅ Database regeneration complete!"
