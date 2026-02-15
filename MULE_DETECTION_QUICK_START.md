# Money Mule Detection - Developer Quick Start

## Installation

```bash
cd TriNetra/backend
source venv/bin/activate  # Activate virtual environment
pip install -r ../requirements.txt
```

## Running the Server

```bash
cd TriNetra/backend
source venv/bin/activate
python app.py
```

Server starts at: `http://localhost:5000`

## Running Tests

```bash
cd TriNetra/backend
source venv/bin/activate
python test_mule_features.py
```

## API Endpoints

### Base URL: `/api/mule`

#### 1. Get Mule Risk Score
```bash
GET /api/mule/mule-risk/<account_id>

Response:
{
  "account_id": "MULE_TEST_001",
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "components": {
    "behavioral_score": 80.0,
    "network_score": 65.0,
    "layering_score": 85.0,
    "velocity_score": 70.0
  },
  "details": { ... }
}
```

#### 2. Get Network Metrics
```bash
GET /api/mule/network-metrics/<account_id>

Response:
{
  "account_id": "MULE_TEST_001",
  "metrics": {
    "degree_centrality": 0.45,
    "betweenness_centrality": 0.23,
    "pagerank": 0.05
  },
  "is_hub": true,
  "is_funnel": false
}
```

#### 3. Get Layering Detection
```bash
GET /api/mule/layering-detection/<account_id>

Response:
{
  "account_id": "MULE_TEST_001",
  "multi_hop_paths": 3,
  "circular_flows": 1,
  "structuring_patterns": 2,
  "layering_risk_score": 0.75
}
```

#### 4. Get Risk Explanation
```bash
GET /api/mule/explain-risk/<account_id>

Response:
{
  "account_id": "MULE_TEST_001",
  "risk_score": 75.5,
  "top_reasons": [
    "High betweenness centrality in network",
    "Rapid in-out transaction pattern",
    "Structuring pattern detected"
  ]
}
```

#### 5. Generate SAR (Suspicious Activity Report)
```bash
POST /api/mule/generate-mule-sar/<account_id>?format=json
POST /api/mule/generate-mule-sar/<account_id>?format=summary

Response (summary):
SUSPICIOUS ACTIVITY REPORT - MULE ACCOUNT
SAR ID: SAR-MULE-20260215123456
Generated: 2026-02-15T12:34:56

ACCOUNT: MULE_TEST_001
RISK SCORE: 75/100 (HIGH)

PRIMARY CONCERNS:
  • Rapid in-out transaction pattern
  • Hub-and-spoke distribution pattern
  • Structuring detected

FATF RED FLAGS:
  • [HIGH] Structuring: Multiple transactions below threshold
  • [HIGH] Rapid Pass-Through: Immediate fund transfers
  ...
```

#### 6. Get Behavioral Profile
```bash
GET /api/mule/behavioral-profile/<account_id>

Response:
{
  "account_id": "MULE_TEST_001",
  "features": {
    "transaction_velocity": 5.2,
    "rapid_in_out": true,
    "dormant_activation_flag": false
  },
  "mule_pattern_score": 0.78
}
```

#### 7. Get Network Visualization Data
```bash
GET /api/mule/network-visualization

Response:
{
  "nodes": [
    {"id": "ACC_001", "degree": 15, "betweenness": 0.23},
    {"id": "ACC_002", "degree": 3, "betweenness": 0.01}
  ],
  "links": [
    {"source": "ACC_001", "target": "ACC_002", "weight": 50000}
  ]
}
```

#### 8. Get High-Risk Accounts
```bash
GET /api/mule/high-risk-accounts?threshold=70&limit=50

Response:
{
  "threshold": 70,
  "count": 12,
  "accounts": [
    {
      "account_id": "MULE_001",
      "risk_score": 85.5,
      "last_updated": "2026-02-15T12:00:00"
    }
  ]
}
```

#### 9. Detect Patterns
```bash
GET /api/mule/detect-patterns?type=all
GET /api/mule/detect-patterns?type=hub-spoke
GET /api/mule/detect-patterns?type=funnel
GET /api/mule/detect-patterns?type=layering
GET /api/mule/detect-patterns?type=circular
GET /api/mule/detect-patterns?type=structuring

Response:
{
  "hub_and_spoke": [
    {"account_id": "HUB_001", "out_degree": 25, "spoke_count": 20}
  ],
  "funnels": [
    {"account_id": "FUNNEL_001", "in_degree": 15, "out_degree": 1}
  ],
  "layering_chains": [...],
  "circular_flows": [...],
  "structuring": [...]
}
```

#### 10. Batch Risk Update
```bash
POST /api/mule/batch-risk-update
Content-Type: application/json

{
  "account_ids": ["ACC_001", "ACC_002", "ACC_003"]
}

Response:
{
  "status": "completed",
  "accounts_updated": 3
}
```

#### 11. Get Statistics
```bash
GET /api/mule/statistics

Response:
{
  "risk_levels": {
    "critical": 15,
    "high": 42,
    "total_high_risk": 57
  },
  "patterns_detected": {
    "hub_and_spoke": 8,
    "funnels": 12,
    "circular_flows": 5,
    "structuring": 18
  },
  "network_stats": {
    "total_nodes": 500,
    "total_edges": 1250
  }
}
```

## Python Usage Examples

### Import Services
```python
from services.mule_behavior_engine import MuleBehaviorEngine
from services.network_engine import NetworkEngine
from services.risk_scoring_engine import RiskScoringEngine
from services.auto_sar import MuleAutoSAR

# Initialize
behavior_engine = MuleBehaviorEngine()
network_engine = NetworkEngine()
risk_engine = RiskScoringEngine()
sar_generator = MuleAutoSAR()
```

### Analyze Account
```python
# Get behavioral features
analysis = behavior_engine.analyze_account("ACC_001")
print(f"Mule Score: {analysis['mule_pattern_score']}")

# Get network metrics
network = network_engine.analyze_account_network("ACC_001")
print(f"Betweenness: {network['metrics']['betweenness_centrality']}")

# Calculate risk
risk = risk_engine.calculate_mule_risk("ACC_001")
print(f"Risk Score: {risk['risk_score']}/100")

# Generate SAR
sar = sar_generator.generate_mule_sar("ACC_001")
print(sar_generator.generate_sar_summary("ACC_001"))
```

### Build Transaction Graph
```python
from services.network_engine import NetworkEngine

engine = NetworkEngine()
graph = engine.build_transaction_graph()

# Detect patterns
hubs = engine.detect_hub_and_spoke(graph)
funnels = engine.detect_funnel_accounts(graph)

print(f"Found {len(hubs)} hub-and-spoke patterns")
print(f"Found {len(funnels)} funnel accounts")
```

### Detect Layering
```python
from services.layering_engine import LayeringEngine

engine = LayeringEngine()

# Detect multi-hop paths
multi_hop = engine.detect_multi_hop_paths(time_window_hours=24)
print(f"Found {len(multi_hop)} multi-hop paths")

# Detect circular flows
circular = engine.detect_circular_flows()
print(f"Found {len(circular)} circular flows")

# Detect structuring
structuring = engine.detect_structuring()
print(f"Found {len(structuring)} structuring patterns")
```

## Configuration

Edit `backend/config.py` to adjust:

```python
# Risk thresholds
HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 50

# Detection parameters
HUB_THRESHOLD = 10
FUNNEL_THRESHOLD = 5
STRUCTURING_THRESHOLD = 49000
```

## Database

### Tables
- `transactions` - All transaction data
- `accounts` - Account information
- `account_risk_scores` - Cached risk scores

### Query Risk Scores
```python
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
cursor = conn.cursor()

cursor.execute('''
    SELECT account_id, risk_score 
    FROM account_risk_scores 
    WHERE risk_score >= 70
    ORDER BY risk_score DESC
''')

high_risk = cursor.fetchall()
conn.close()
```

## Troubleshooting

### NumPy Version Issue
If you get NumPy compatibility errors with SHAP:
```bash
pip install "numpy<2"
```

### Database Not Found
Initialize database:
```bash
python -c "from data.synthetic_generator import init_database; init_database()"
```

### Import Errors
Ensure you're in the correct directory and venv is activated:
```bash
cd TriNetra/backend
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Performance Tips

1. **For large graphs (1000+ nodes):**
   - Network analysis uses sampling
   - Adjust sample size in `network_engine.py`

2. **Batch processing:**
   - Use `/api/mule/batch-risk-update` for multiple accounts
   - Process in chunks of 100 accounts

3. **Caching:**
   - Risk scores are cached in database
   - Use stored scores when real-time update not needed

## Support

For issues or questions:
1. Check test file: `test_mule_features.py`
2. Review implementation: `MULE_DETECTION_IMPLEMENTATION.md`
3. See API docs above

---

**Last Updated:** 2026-02-15
