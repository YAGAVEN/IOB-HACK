#!/bin/bash

echo "🔄 Restarting TriNetra Backend with SQLite..."

# Find and kill existing backend process
echo "Stopping existing backend process..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

# Start backend
cd /media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/backend
source venv/bin/activate

echo "Starting backend..."
python app.py &
BACKEND_PID=$!

echo "✅ Backend restarted (PID: $BACKEND_PID)"
echo ""

# Wait for backend to start
sleep 3

# Test the API
echo "🔍 Testing API..."
response=$(curl -s http://localhost:5001/api/chronos/timeline?time_quantum=1m)
if echo "$response" | grep -q '"status":"success"'; then
    echo "✅ API is working!"
    echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Total transactions: {data.get('total_transactions', 0)}\")"
else
    echo "❌ API test failed:"
    echo "$response"
fi

echo ""
echo "💡 Backend is running in the background"
echo "💡 Access at: http://localhost:5001"
echo "💡 To stop: pkill -f 'python.*app.py'"
