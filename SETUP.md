# TriNetra AML Platform - Setup Guide

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)

**TriNetra** is an advanced Anti-Money Laundering (AML) platform with money mule detection capabilities, featuring behavioral profiling, network analysis, and AI-powered risk scoring.

---

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## ✨ Features

### Existing Features
- **CHRONOS** - Transaction timeline analysis and pattern detection
- **HYDRA** - GAN-based adversarial pattern generation
- **AUTOSAR** - Automated Suspicious Activity Report generation

### New Money Mule Detection Features
- **Behavioral Profiling Engine** - Detect rapid in-out, dormant activation, structuring
- **Network Analysis Engine** - Graph-based centrality, hub-spoke, funnel detection
- **Layering Detection** - Multi-hop paths, circular flows, threshold avoidance
- **Real-Time Risk Scoring** - Weighted multi-component risk assessment (0-100)
- **Explainable AI** - SHAP-based risk explanations
- **Mule-Specific Auto-SAR** - FATF-compliant suspicious activity reports

---

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Python 3.8+** (Python 3.12 recommended)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### Optional
- **Virtual Environment** (recommended)
- **curl** (for testing API endpoints)

### Check Your Installation

```bash
# Check Python version
python3 --version
# Should output: Python 3.8 or higher

# Check pip
pip3 --version
# Should output pip version

# Check Git
git --version
# Should output git version
```

---

## 🚀 Quick Start

For those who want to get started immediately:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/IOB-HACK.git
cd IOB-HACK

# 2. Navigate to backend
cd TriNetra/backend

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r ../requirements.txt

# 5. Run the application
python app.py

# 6. Access the application
# Open browser: http://localhost:5001
```

That's it! The server is now running with all features.

---

## 📦 Detailed Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/IOB-HACK.git
cd IOB-HACK
```

### Step 2: Navigate to Backend Directory

```bash
cd TriNetra/backend
```

### Step 3: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### Step 4: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r ../requirements.txt
```

**Expected packages installed:**
- Flask 2.3.3
- Flask-CORS 4.0.0
- pandas 2.1.0
- numpy <2 (for SHAP compatibility)
- scikit-learn 1.3.0
- networkx 3.1
- shap 0.42.1
- python-louvain
- And more...

### Step 5: Verify Installation

```bash
python -c "import flask, pandas, networkx, shap; print('✅ All packages installed successfully')"
```

If you see the success message, you're good to go!

---

## 🏃 Running the Application

### Start the Server

```bash
# Make sure you're in TriNetra/backend directory
cd TriNetra/backend

# Activate virtual environment (if not already activated)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python app.py
```

**Expected Output:**
```
✅ Database already contains XXX transactions
🔹 TriNetra Backend Starting...
🔹 Server running at: http://localhost:5001
🔹 Press Ctrl+C to stop
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5001
```

### Access the Application

- **Frontend:** http://localhost:5001
- **API Base:** http://localhost:5001/api
- **Health Check:** http://localhost:5001/api/health

### Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## 🧪 Testing

### Run Test Suite

```bash
# Make sure you're in TriNetra/backend directory
cd TriNetra/backend
source venv/bin/activate

# Run comprehensive mule detection tests
python test_mule_features.py
```

**Expected Output:**
```
================================================================================
TRINETRA MULE DETECTION FEATURES - TEST
================================================================================

1. Initializing database...
   ✓ Database initialized

2. Generating test mule transaction patterns...
   ✓ Generated 11 test transactions

3. Testing Mule Behavioral Profiling Engine...
   ✓ Behavioral analysis completed

...

TEST COMPLETED
All mule detection features are implemented and functional!
```

### Test API Endpoints

With the server running, open a new terminal:

```bash
# Test health check
curl http://localhost:5001/api/health

# Test mule risk scoring
curl http://localhost:5001/api/mule/mule-risk/MULE_TEST_001

# Test statistics
curl http://localhost:5001/api/mule/statistics

# Generate SAR (Suspicious Activity Report)
curl -X POST http://localhost:5001/api/mule/generate-mule-sar/MULE_TEST_001?format=summary
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:5001/api
```

### Existing Features

#### CHRONOS API (`/api/chronos`)
```bash
GET  /api/chronos/timeline           # Transaction timeline
GET  /api/chronos/patterns           # Pattern detection
POST /api/chronos/search             # Search transactions
```

#### HYDRA API (`/api/hydra`)
```bash
GET  /api/hydra/simulation           # GAN simulation
POST /api/hydra/generate             # Generate patterns
POST /api/hydra/detect               # Detect patterns
```

#### AUTOSAR API (`/api/autosar`)
```bash
GET  /api/autosar/templates          # SAR templates
POST /api/autosar/generate           # Generate SAR
POST /api/autosar/location-mapping   # Location mapping
```

### New Mule Detection API (`/api/mule`)

#### Risk Assessment
```bash
GET /api/mule/mule-risk/<account_id>
# Returns: Complete risk assessment with 0-100 score

Example:
curl http://localhost:5001/api/mule/mule-risk/ACC_001

Response:
{
  "account_id": "ACC_001",
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "components": {
    "behavioral_score": 80.0,
    "network_score": 65.0,
    "layering_score": 85.0,
    "velocity_score": 70.0
  }
}
```

#### Network Analysis
```bash
GET /api/mule/network-metrics/<account_id>
# Returns: Network centrality metrics, hub/funnel detection

GET /api/mule/network-visualization
# Returns: D3.js-ready network data (nodes & links)
```

#### Layering Detection
```bash
GET /api/mule/layering-detection/<account_id>
# Returns: Multi-hop paths, circular flows, structuring patterns
```

#### Explainability
```bash
GET /api/mule/explain-risk/<account_id>
# Returns: Top contributing factors to risk score

Example:
curl http://localhost:5001/api/mule/explain-risk/ACC_001

Response:
{
  "account_id": "ACC_001",
  "risk_score": 75.5,
  "top_reasons": [
    "High betweenness centrality in network",
    "Rapid in-out transaction pattern",
    "Structuring pattern detected"
  ]
}
```

#### SAR Generation
```bash
POST /api/mule/generate-mule-sar/<account_id>?format=json
POST /api/mule/generate-mule-sar/<account_id>?format=summary
# Returns: FATF-compliant Suspicious Activity Report

Example:
curl -X POST "http://localhost:5001/api/mule/generate-mule-sar/ACC_001?format=summary"
```

#### High-Risk Accounts
```bash
GET /api/mule/high-risk-accounts?threshold=70&limit=50
# Returns: List of accounts above risk threshold

Example:
curl "http://localhost:5001/api/mule/high-risk-accounts?threshold=70&limit=20"
```

#### Pattern Detection
```bash
GET /api/mule/detect-patterns?type=all
GET /api/mule/detect-patterns?type=hub-spoke
GET /api/mule/detect-patterns?type=funnel
GET /api/mule/detect-patterns?type=layering
GET /api/mule/detect-patterns?type=circular
GET /api/mule/detect-patterns?type=structuring
# Returns: Detected patterns across all accounts
```

#### Statistics
```bash
GET /api/mule/statistics
# Returns: Overall detection statistics

Example Response:
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
  }
}
```

#### Batch Operations
```bash
POST /api/mule/batch-risk-update
Content-Type: application/json

{
  "account_ids": ["ACC_001", "ACC_002", "ACC_003"]
}
# Returns: Number of accounts updated
```

### Complete Endpoint List

| Method | Endpoint | Description |
|--------|----------|-------------|
| **General** | | |
| GET | `/api/health` | Health check |
| **CHRONOS** | | |
| GET | `/api/chronos/timeline` | Transaction timeline |
| GET | `/api/chronos/patterns` | Pattern analysis |
| POST | `/api/chronos/search` | Search transactions |
| **HYDRA** | | |
| GET | `/api/hydra/simulation` | GAN simulation |
| POST | `/api/hydra/generate` | Generate patterns |
| POST | `/api/hydra/detect` | Detect patterns |
| **AUTOSAR** | | |
| GET | `/api/autosar/templates` | SAR templates |
| POST | `/api/autosar/generate` | Generate SAR |
| POST | `/api/autosar/location-mapping` | Location mapping |
| **MULE** | | |
| GET | `/api/mule/mule-risk/<id>` | Risk assessment |
| GET | `/api/mule/network-metrics/<id>` | Network metrics |
| GET | `/api/mule/layering-detection/<id>` | Layering analysis |
| GET | `/api/mule/explain-risk/<id>` | Risk explanation |
| POST | `/api/mule/generate-mule-sar/<id>` | Generate SAR |
| GET | `/api/mule/behavioral-profile/<id>` | Behavioral features |
| GET | `/api/mule/network-visualization` | Network graph data |
| GET | `/api/mule/high-risk-accounts` | High-risk list |
| GET | `/api/mule/detect-patterns` | Pattern detection |
| POST | `/api/mule/batch-risk-update` | Batch update |
| GET | `/api/mule/statistics` | Overall stats |

---

## 🔧 Troubleshooting

### Issue: NumPy Version Conflict

**Error:**
```
ImportError: A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x
```

**Solution:**
```bash
pip install "numpy<2"
```

### Issue: SHAP Import Error

**Error:**
```
ImportError: cannot import name 'shap'
```

**Solution:**
```bash
pip install shap==0.42.1 "numpy<2"
```

### Issue: Database Not Found

**Error:**
```
sqlite3.OperationalError: no such table: transactions
```

**Solution:**
The database is automatically created on first run. If issues persist:
```bash
cd TriNetra/backend
python -c "from data.synthetic_generator import init_database; init_database()"
```

### Issue: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 5001
lsof -i :5001  # On Linux/macOS
netstat -ano | findstr :5001  # On Windows

# Kill the process or change port in config.py
```

### Issue: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
Ensure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r ../requirements.txt
```

### Issue: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Ensure you have write permissions
chmod -R u+w TriNetra/

# Or run without sudo (never use sudo with pip)
```

### Common Checks

```bash
# Verify Python version
python3 --version  # Should be 3.8+

# Verify virtual environment is activated
which python  # Should point to venv/bin/python

# Check installed packages
pip list

# Test imports
python -c "import flask, pandas, networkx; print('OK')"
```

---

## 📁 Project Structure

```
IOB-HACK/
├── TriNetra/
│   ├── backend/
│   │   ├── api/                      # API Blueprints
│   │   │   ├── chronos_api.py       # CHRONOS endpoints
│   │   │   ├── hydra_api.py         # HYDRA endpoints
│   │   │   ├── autosar_api.py       # AUTOSAR endpoints
│   │   │   └── mule_api.py          # Mule detection endpoints ✨
│   │   ├── services/                 # Service Layer (NEW) ✨
│   │   │   ├── mule_behavior_engine.py
│   │   │   ├── network_engine.py
│   │   │   ├── layering_engine.py
│   │   │   ├── risk_scoring_engine.py
│   │   │   ├── explainability_engine.py
│   │   │   └── auto_sar.py
│   │   ├── data/                     # Data Layer
│   │   │   └── synthetic_generator.py
│   │   ├── models/                   # Data Models
│   │   ├── utils/                    # Utilities
│   │   ├── app.py                    # Main Flask Application
│   │   ├── config.py                 # Configuration
│   │   ├── test_mule_features.py    # Test Suite ✨
│   │   └── venv/                     # Virtual Environment
│   ├── frontend/                     # Frontend Files
│   └── requirements.txt              # Python Dependencies
├── SETUP.md                          # This file
├── README.md                         # Project README
├── MULE_DETECTION_IMPLEMENTATION.md # Feature docs ✨
├── MULE_DETECTION_QUICK_START.md   # Quick reference ✨
└── ARCHITECTURE_EXPLANATION.md      # Architecture docs ✨
```

---

## 🗄️ Database Schema

The application uses SQLite with the following tables:

### `transactions`
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE,
    from_account TEXT,
    to_account TEXT,
    amount REAL,
    timestamp TEXT,
    transaction_type TEXT,
    suspicious_score REAL,
    pattern_type TEXT,
    scenario TEXT
);
```

### `accounts`
```sql
CREATE TABLE accounts (
    account_id TEXT PRIMARY KEY,
    account_name TEXT,
    account_type TEXT,
    country TEXT,
    risk_level TEXT
);
```

### `account_risk_scores` (NEW)
```sql
CREATE TABLE account_risk_scores (
    account_id TEXT PRIMARY KEY,
    risk_score REAL,
    last_updated TEXT
);
```

---

## 🔐 Configuration

Edit `TriNetra/backend/config.py` to customize:

```python
class Config:
    # Server settings
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = True
    
    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'trinetra.db')
    
    # Detection thresholds (can be customized)
    HIGH_RISK_THRESHOLD = 70
    MEDIUM_RISK_THRESHOLD = 50
```

---

## 🚢 Deployment

### Development
```bash
python app.py  # Built-in Flask server (DEBUG=True)
```

### Production

**Using Gunicorn (Recommended):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

**Using uWSGI:**
```bash
pip install uwsgi
uwsgi --http :5001 --wsgi-file app.py --callable app --processes 4
```

**Using Docker:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "app.py"]
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 Development

### Running Tests
```bash
cd TriNetra/backend
source venv/bin/activate
python test_mule_features.py
```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

### Adding New Features
1. Create service in `services/` directory
2. Create API blueprint in `api/` directory
3. Register blueprint in `app.py`
4. Add tests in `test_*.py`
5. Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- FATF guidelines for AML compliance
- NetworkX for graph analysis
- SHAP for explainable AI
- Flask community for the excellent web framework

---

## 📞 Support

For issues and questions:

1. **Check Troubleshooting Section** above
2. **Read Documentation**:
   - `MULE_DETECTION_IMPLEMENTATION.md` - Detailed feature docs
   - `MULE_DETECTION_QUICK_START.md` - Quick reference
   - `ARCHITECTURE_EXPLANATION.md` - Architecture overview
3. **Open an Issue** on GitHub
4. **Check Logs** - Server output often contains helpful error messages

---

## 🎯 Quick Links

- [Feature Documentation](MULE_DETECTION_IMPLEMENTATION.md)
- [Quick Start Guide](MULE_DETECTION_QUICK_START.md)
- [Architecture Explanation](ARCHITECTURE_EXPLANATION.md)
- [API Reference](#api-documentation)

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Server starts without errors
- [ ] Database is created
- [ ] Health check responds: `curl http://localhost:5001/api/health`
- [ ] Test suite passes: `python test_mule_features.py`
- [ ] Existing APIs work: `curl http://localhost:5001/api/chronos/timeline`
- [ ] New Mule APIs work: `curl http://localhost:5001/api/mule/statistics`

---

**Happy Coding! 🚀**

If you find this project useful, please ⭐ star the repository!
