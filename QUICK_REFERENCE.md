# TriNetra AML Platform - Quick Reference Card

## 🚀 One-Line Setup

```bash
git clone <repo> && cd IOB-HACK/TriNetra/backend && python3 -m venv venv && source venv/bin/activate && pip install -r ../requirements.txt && python app.py
```

## 📍 Key URLs

- **Application**: http://localhost:5001
- **API Base**: http://localhost:5001/api
- **Health Check**: http://localhost:5001/api/health

## 🎯 Essential Commands

### Setup
```bash
cd TriNetra/backend
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
```

### Run
```bash
python app.py               # Start server
python test_mule_features.py  # Run tests
```

### Test APIs
```bash
# Health check
curl http://localhost:5001/api/health

# Statistics
curl http://localhost:5001/api/mule/statistics

# Risk score
curl http://localhost:5001/api/mule/mule-risk/ACC_001

# Generate SAR
curl -X POST http://localhost:5001/api/mule/generate-mule-sar/ACC_001?format=summary
```

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `SETUP.md` | **START HERE** - Complete setup guide |
| `MULE_DETECTION_IMPLEMENTATION.md` | Feature details |
| `ARCHITECTURE_EXPLANATION.md` | How it works |

## 🔧 Troubleshooting Quick Fixes

```bash
# NumPy version issue
pip install "numpy<2"

# Database not found
python -c "from data.synthetic_generator import init_database; init_database()"

# Port in use
# Change PORT in config.py or kill process on 5001

# Module not found
source venv/bin/activate
pip install -r ../requirements.txt
```

## 📊 API Endpoints (Quick List)

### Mule Detection (`/api/mule`)
```
GET  /mule-risk/<id>              # Risk score
GET  /network-metrics/<id>        # Network analysis
GET  /layering-detection/<id>     # Layering patterns
GET  /explain-risk/<id>           # Explanations
POST /generate-mule-sar/<id>      # Generate SAR
GET  /high-risk-accounts          # High-risk list
GET  /statistics                  # Overall stats
```

### Existing Features
```
GET  /chronos/timeline            # Transaction timeline
GET  /hydra/simulation            # GAN patterns
POST /autosar/generate            # SAR generation
```

## 🎯 Detection Patterns (8 Types)

1. Rapid Pass-Through
2. Hub-and-Spoke
3. Funnel Account
4. Multi-Hop Layering
5. Circular Flows
6. Structuring
7. Dormant Activation
8. Small→Large Pattern

## 📈 Risk Levels

- **CRITICAL**: 70-100
- **HIGH**: 50-69
- **MEDIUM**: 30-49
- **LOW**: 0-29

## 🔑 Key Features

✅ 5 Detection Engines  
✅ 11 New API Endpoints  
✅ 8 Pattern Types  
✅ SHAP Explainability  
✅ FATF Compliance  
✅ Real-Time Scoring  
✅ Auto-SAR Generation  

## 📞 Get Help

1. Check `SETUP.md` troubleshooting section
2. Run `python test_mule_features.py`
3. Check server logs
4. Open GitHub issue

---

**Version**: 1.0.0 | **Status**: Production Ready | **Updated**: Feb 2026
