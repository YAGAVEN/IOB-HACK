# TriNetra Architecture - Integrated Yet Modular

## Current Architecture: INTEGRATED BUT MODULAR ✅

The additional features (mule detection) and existing features run on the **SAME server** but are **logically separated** with **independent modules**.

```
┌─────────────────────────────────────────────────────────────┐
│                    SINGLE FLASK SERVER                       │
│                  http://localhost:5001                       │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┬─────────────────┐
            │               │               │                 │
            ▼               ▼               ▼                 ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   CHRONOS    │ │    HYDRA     │ │   AUTOSAR    │ │     MULE     │
    │  (Existing)  │ │  (Existing)  │ │  (Existing)  │ │    (NEW)     │
    └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         │                │                │                 │
         │                │                │                 │
    /api/chronos     /api/hydra      /api/autosar      /api/mule
         │                │                │                 │
         │                │                │                 │
         └────────────────┴────────────────┴─────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    SHARED DATABASE      │
                    │   (trinetra.db)         │
                    │                         │
                    │  • transactions         │
                    │  • accounts             │
                    │  • account_risk_scores  │
                    └─────────────────────────┘
```

## Feature Separation

### ✅ EXISTING Features (Unchanged)
```
/api/chronos/*     - Timeline analysis, transaction patterns
/api/hydra/*       - GAN-based pattern generation
/api/autosar/*     - Auto-SAR generation (original)
```

### ✅ NEW Mule Detection Features (Added)
```
/api/mule/*        - All mule detection endpoints (11 total)
    ├── /mule-risk/<account_id>
    ├── /network-metrics/<account_id>
    ├── /layering-detection/<account_id>
    ├── /explain-risk/<account_id>
    ├── /generate-mule-sar/<account_id>
    ├── /behavioral-profile/<account_id>
    ├── /network-visualization
    ├── /high-risk-accounts
    ├── /detect-patterns
    ├── /batch-risk-update
    └── /statistics
```

## How They Work Together

### SHARED Resources
- ✅ **Same Flask App** - Single server process
- ✅ **Same Database** - All features read from same transactions table
- ✅ **Same Port** - http://localhost:5001
- ✅ **Same CORS** - All features accessible from frontend

### SEPARATE Modules
- ✅ **Different URL prefixes** - No conflicts
- ✅ **Independent services** - Each has own service layer
- ✅ **Isolated logic** - Mule features don't affect existing features
- ✅ **Can run independently** - Each API works on its own

## File Organization

```
TriNetra/backend/
│
├── app.py                    # Main Flask app (registers ALL blueprints)
│
├── api/                      # API Layer (All Blueprints)
│   ├── chronos_api.py       # EXISTING - Timeline API
│   ├── hydra_api.py         # EXISTING - GAN API
│   ├── autosar_api.py       # EXISTING - Auto-SAR API
│   └── mule_api.py          # NEW - Mule Detection API ✨
│
├── services/                 # NEW - Service Layer for Mule
│   ├── mule_behavior_engine.py
│   ├── network_engine.py
│   ├── layering_engine.py
│   ├── risk_scoring_engine.py
│   ├── explainability_engine.py
│   └── auto_sar.py
│
├── data/                     # SHARED - Data layer
│   └── synthetic_generator.py
│
└── config.py                 # SHARED - Configuration
```

## Database Schema

```sql
-- EXISTING TABLES (Used by all features)
transactions (
    id, transaction_id, from_account, to_account,
    amount, timestamp, transaction_type,
    suspicious_score, pattern_type, scenario
)

accounts (
    account_id, account_name, account_type,
    country, risk_level
)

-- NEW TABLE (Used by mule detection)
account_risk_scores (
    account_id, risk_score, last_updated
)
```

## Integration Benefits

### ✅ Advantages of This Architecture

1. **Single Deployment** - One server to run
2. **Shared Data** - All features analyze same transactions
3. **No Conflicts** - Different URL prefixes prevent collisions
4. **Easy Frontend** - One API base URL
5. **Combined Power** - Can use both existing and new features together

### ✅ Independence Benefits

1. **Modular** - Mule features can be disabled without affecting others
2. **Separate Testing** - Each module tests independently
3. **Clean Code** - No mixing of concerns
4. **Easy Updates** - Update one module without touching others

## How to Use

### Use Existing Features (Still Work Exactly the Same)
```bash
# Timeline analysis
curl http://localhost:5001/api/chronos/timeline

# GAN patterns
curl http://localhost:5001/api/hydra/generate-pattern

# Auto-SAR (original)
curl http://localhost:5001/api/autosar/generate-sar
```

### Use NEW Mule Features
```bash
# Mule risk assessment
curl http://localhost:5001/api/mule/mule-risk/ACC_001

# Network analysis
curl http://localhost:5001/api/mule/network-metrics/ACC_001

# Mule-specific SAR
curl -X POST http://localhost:5001/api/mule/generate-mule-sar/ACC_001
```

### Use Both Together (Combined Analysis)
```bash
# Get timeline from CHRONOS
curl http://localhost:5001/api/chronos/timeline?account=ACC_001

# Get mule risk for same account
curl http://localhost:5001/api/mule/mule-risk/ACC_001

# Generate comprehensive report using both
```

## Running the System

### Single Server Runs Everything
```bash
cd TriNetra/backend
source venv/bin/activate
python app.py

# This starts ONE server with ALL features:
# ✅ CHRONOS (existing)
# ✅ HYDRA (existing)
# ✅ AUTOSAR (existing)
# ✅ MULE (new)
```

## Testing

### Test Existing Features (Should Still Work)
```bash
# These should work exactly as before
curl http://localhost:5001/api/chronos/timeline
curl http://localhost:5001/api/health
```

### Test New Features
```bash
# These are the new additions
curl http://localhost:5001/api/mule/statistics
curl http://localhost:5001/api/mule/high-risk-accounts
```

## Summary

| Aspect | Status |
|--------|--------|
| **Server** | SHARED - Single Flask server |
| **Port** | SHARED - Same port (5001) |
| **Database** | SHARED - Same SQLite database |
| **API Endpoints** | SEPARATE - Different URL prefixes |
| **Service Logic** | SEPARATE - Independent modules |
| **Can Disable Mule** | YES - Remove mule_bp registration |
| **Can Use Together** | YES - All features accessible |

## Answer to Your Question

**Are they running separately?**

- ❌ **NOT separate servers** - All run on ONE Flask server
- ✅ **Separate API routes** - Different URL paths (`/api/chronos` vs `/api/mule`)
- ✅ **Separate code modules** - Independent service files
- ✅ **Can work independently** - Don't interfere with each other
- ✅ **Share same data** - Both read from same database

**Think of it like:**
- One restaurant (server)
- Different menus (API blueprints)
- Same kitchen (database)
- Each menu can be ordered independently
- All served from same location

## If You Want Truly Separate Servers

If you need them to run on different servers, you can:

```bash
# Server 1 - Existing features only
# Comment out: app.register_blueprint(mule_bp, ...)
python app.py  # Runs on port 5001

# Server 2 - Mule features only
# Create new app with only mule_bp
python app_mule.py  # Runs on port 5002
```

But **currently**, they are **integrated into one server** for simplicity and better data sharing. This is the **recommended architecture** for most use cases.
