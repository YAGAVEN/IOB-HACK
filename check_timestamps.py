import sqlite3
from datetime import datetime, timedelta

db_path = '/media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/backend/data/transactions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check date range of transactions
cursor.execute('SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM transactions')
min_date, max_date, count = cursor.fetchone()

print(f"Total transactions: {count}")
print(f"Date range: {min_date} to {max_date}")
print()

# Check how many are within last 30 days
now = datetime.now()
thirty_days_ago = now - timedelta(days=30)
print(f"Current time: {now.isoformat()}")
print(f"30 days ago: {thirty_days_ago.isoformat()}")
print()

cursor.execute('SELECT COUNT(*) FROM transactions WHERE timestamp >= ?', (thirty_days_ago.isoformat(),))
recent_count = cursor.fetchone()[0]
print(f"Transactions in last 30 days: {recent_count}")

# Show some sample timestamps
cursor.execute('SELECT transaction_id, timestamp FROM transactions ORDER BY timestamp DESC LIMIT 5')
print("\nMost recent 5 transactions:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
