#!/usr/bin/env python3
"""Regenerate the database with fresh data"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/backend')

from data.synthetic_generator import TriNetraDataGenerator
from config import Config

print("🔄 Regenerating TriNetra database with fresh timestamps...")
print(f"Database path: {Config.DATABASE_PATH}")

generator = TriNetraDataGenerator(Config.DATABASE_PATH)
generator.create_tables()
generator.populate_database()

print("✅ Database regenerated successfully!")

# Verify
import sqlite3
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
recent = cursor.fetchone()[0]
print(f"   Transactions (last 30 days): {recent}")

conn.close()
