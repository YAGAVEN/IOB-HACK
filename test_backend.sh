#!/bin/bash

echo "=== Testing TriNetra Backend API ==="
echo ""

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
    curl -s http://localhost:5001/api/health | python3 -m json.tool
else
    echo "❌ Backend is NOT running"
    echo "Please start the backend first:"
    echo "   cd TriNetra/backend"
    echo "   source venv/bin/activate"
    echo "   python app.py"
    exit 1
fi

echo ""
echo "2. Testing CHRONOS timeline endpoint..."
response=$(curl -s http://localhost:5001/api/chronos/timeline?time_quantum=1m)
if echo "$response" | grep -q "status"; then
    echo "✅ CHRONOS endpoint responding"
    echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Total transactions: {data.get('total_transactions', 0)}\")"
else
    echo "❌ CHRONOS endpoint failed"
    echo "$response"
fi

echo ""
echo "3. Testing database transactions..."
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('TriNetra/backend/data/transactions.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM transactions')
count = cursor.fetchone()[0]
cursor.execute('SELECT * FROM transactions LIMIT 1')
row = cursor.fetchone()
conn.close()
print(f"✅ Database has {count} transactions")
if row:
    print(f"Sample transaction: {row[0]} - Amount: ${row[3]}")
EOF

echo ""
echo "=== Diagnosis Complete ==="
