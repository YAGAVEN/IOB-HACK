import sqlite3
import json
import os

db_path = '/media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/backend/data/transactions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get sample transactions
cursor.execute('SELECT * FROM transactions LIMIT 3')
cols = [desc[0] for desc in cursor.description]
rows = cursor.fetchall()

print("Sample Transactions:")
for row in rows:
    print(json.dumps(dict(zip(cols, row)), indent=2))
    print("-" * 50)

conn.close()
