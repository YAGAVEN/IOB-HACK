#!/bin/bash

echo "=========================================="
echo "TriNetra Mule Detection API Demo"
echo "=========================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "❌ Server not running. Start it with:"
    echo "   cd TriNetra/backend && source venv/bin/activate && python app.py"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Test account
ACCOUNT="MULE_TEST_001"

echo "Testing Mule Detection APIs for account: $ACCOUNT"
echo ""

echo "1️⃣  Getting Risk Score..."
curl -s http://localhost:5001/api/mule/mule-risk/$ACCOUNT | python3 -m json.tool | head -20
echo ""

echo "2️⃣  Getting Network Metrics..."
curl -s http://localhost:5001/api/mule/network-metrics/$ACCOUNT | python3 -m json.tool | head -15
echo ""

echo "3️⃣  Getting Statistics..."
curl -s http://localhost:5001/api/mule/statistics | python3 -m json.tool | head -20
echo ""

echo "4️⃣  Generating SAR Summary..."
curl -s -X POST "http://localhost:5001/api/mule/generate-mule-sar/$ACCOUNT?format=summary" | head -30
echo ""

echo "=========================================="
echo "API Demo Complete!"
echo "=========================================="
