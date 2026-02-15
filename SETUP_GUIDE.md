# TriNetra - Financial Crime Detection System
## Complete Setup & Environment Guide

---

## 📋 Project Overview

**TriNetra** is a Financial Crime Detection Application built for the National CyberShield Hackathon 2025.

### Key Features:
- 🕐 **CHRONOS**: Time-lapse transaction visualization
- 🐍 **HYDRA**: AI red-teaming for adversarial testing
- 📋 **Auto-SAR**: Automated Suspicious Activity Report generation

---

## ✅ Prerequisites (Already Installed on Your System)

### System Requirements:
- ✅ **Python 3.12.3** - Installed and working
- ✅ **Node.js v24.13.0** - Installed and working  
- ✅ **npm 11.6.2** - Installed and working

---

## 🚀 Quick Start (Environment Already Set Up!)

The environment has been **successfully configured**. To run the application:

```bash
cd /media/yagaven_25/coding/Projects/IOB-HACK
bash start.sh
```

This will:
- Start the backend Flask server on **http://localhost:5001**
- Start the frontend Vite server on **http://localhost:5175**
- Initialize a SQLite database with 750 sample transactions

### Access Points:
- 🌐 **Frontend**: http://localhost:5175
- ⚙️ **Backend API**: http://localhost:5001
- ❤️ **Health Check**: http://localhost:5001/api/health
- 📱 **Login Page**: http://localhost:5175/login.html
- 🏠 **Dashboard**: http://localhost:5175/dashboard.html

---

## 📦 Installed Dependencies

### Backend (Python - Virtual Environment)
Located: `/media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/backend/venv`

**Packages Installed:**
```
Flask==2.3.3          # Web framework
Flask-CORS==4.0.0     # Cross-Origin Resource Sharing
pandas                # Data manipulation
numpy                 # Numerical computing
scikit-learn          # Machine learning
python-dateutil       # Date utilities
Faker                 # Fake data generation
matplotlib            # Plotting library
seaborn               # Statistical visualization
plotly                # Interactive plots
```

### Frontend (Node.js)
Located: `/media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/frontend/node_modules`

**Packages Installed:**
```json
{
  "vite": "^4.4.9",      // Build tool & dev server
  "d3": "^7.8.5",        // Data visualization
  "chart.js": "^4.4.0"   // Chart library
}
```

---

## 🗂️ Project Structure

```
IOB-HACK/
├── TriNetra/                      # Main application directory
│   ├── backend/                   # Flask backend
│   │   ├── venv/                  # ✅ Python virtual environment (configured)
│   │   ├── app.py                 # Main Flask application
│   │   ├── config.py              # Configuration settings
│   │   ├── api/                   # API endpoints
│   │   │   ├── chronos_api.py     # Timeline analysis API
│   │   │   ├── hydra_api.py       # AI red-team API
│   │   │   └── autosar_api.py     # Report generation API
│   │   ├── data/                  # Data processing
│   │   │   ├── transactions.db    # SQLite database (auto-generated)
│   │   │   └── synthetic_generator.py
│   │   ├── models/                # ML models
│   │   └── utils/                 # Utility functions
│   │
│   ├── frontend/                  # Vite + Vanilla JS frontend
│   │   ├── node_modules/          # ✅ NPM packages (installed)
│   │   ├── index.html             # Main entry page
│   │   ├── login.html             # Login page
│   │   ├── chronos.html           # Timeline visualization
│   │   ├── hydra.html             # AI red-team interface
│   │   ├── autosar.html           # Report generation
│   │   ├── js/                    # JavaScript modules
│   │   ├── css/                   # Stylesheets
│   │   ├── package.json           # NPM configuration
│   │   └── vite.config.js         # Vite configuration
│   │
│   └── README.md                  # Project documentation
│
├── start.sh                       # ✅ Startup script (ready to use)
├── vercel.json                    # Vercel deployment config
└── SETUP_GUIDE.md                 # This file
```

---

## 🔧 Manual Setup (If Needed)

### 1. Backend Setup
```bash
cd /media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/backend

# Create virtual environment (already done)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (already done)
pip install Flask Flask-CORS pandas numpy scikit-learn python-dateutil Faker matplotlib seaborn plotly

# Run backend
python app.py
```

### 2. Frontend Setup
```bash
cd /media/yagaven_25/coding/Projects/IOB-HACK/TriNetra/frontend

# Install dependencies (already done)
npm install

# Run development server
npm run dev
```

---

## 🌐 External Setup Requirements

### ⚠️ NO External Services Required!

This application runs **completely locally** and does NOT require:
- ❌ External databases (uses SQLite)
- ❌ Cloud services
- ❌ API keys
- ❌ Authentication servers
- ❌ Third-party integrations

### Optional (for Production Deployment):

1. **Vercel Deployment** (Frontend Only)
   - Already configured via `vercel.json`
   - Run: `vercel deploy` (requires Vercel CLI)

2. **Production Database** (Optional)
   - Currently uses SQLite (file-based)
   - For production, consider PostgreSQL or MySQL
   - Update `config.py` with connection string

3. **CORS Configuration**
   - Currently allows all origins (development)
   - For production, update Flask-CORS settings in `app.py`

---

## 🧪 Testing the Setup

### 1. Check Backend API
```bash
curl http://localhost:5001/api/health
# Expected: {"service": "TriNetra API", "status": "healthy"}
```

### 2. Check Frontend
```bash
curl -I http://localhost:5175
# Expected: HTTP/1.1 200 OK
```

### 3. Test Database
```bash
cd TriNetra/backend
source venv/bin/activate
python -c "from data.synthetic_generator import init_database; init_database()"
# Expected: Database initialization message
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on port 5001 (backend)
lsof -ti:5001 | xargs kill -9

# Kill processes on port 5175 (frontend)
lsof -ti:5175 | xargs kill -9
```

### Virtual Environment Not Activating
```bash
cd TriNetra/backend
source venv/bin/activate
# Should show (venv) in prompt
```

### NPM Dependencies Issues
```bash
cd TriNetra/frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Issues
```bash
# Remove and regenerate database
cd TriNetra/backend
rm -f data/transactions.db
python -c "from data.synthetic_generator import init_database; init_database()"
```

---

## 📊 Technology Stack

### Backend:
- **Framework**: Flask 2.3.3
- **Database**: SQLite (local file-based)
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Visualization**: Matplotlib, Seaborn, Plotly

### Frontend:
- **Build Tool**: Vite 4.4.9
- **UI**: Vanilla JavaScript (ES6+)
- **Visualization**: D3.js 7.8.5, Chart.js 4.4.0
- **PWA**: Service Worker + Web Manifest

### DevOps:
- **Version Control**: Git
- **Deployment**: Vercel (Frontend)
- **Development**: Hot Module Replacement (HMR)

---

## 🎯 Next Steps

1. **Start the Application**:
   ```bash
   bash start.sh
   ```

2. **Access the Dashboard**:
   - Open browser: http://localhost:5175

3. **Explore Features**:
   - CHRONOS Timeline Analysis
   - HYDRA AI Red-Team Battle
   - Auto-SAR Report Generation

4. **Development**:
   - Backend changes: Auto-reload enabled
   - Frontend changes: HMR enabled (instant updates)

---

## 📝 Notes

- ✅ **Environment fully configured and tested**
- ✅ **Database initialized with 750 sample transactions**
- ✅ **All dependencies installed and verified**
- ✅ **Application successfully tested and running**
- ⚡ **Ready for development and demonstration**

---

## 🤝 Support

For issues or questions:
- Check logs in terminal output
- Review `TriNetra/README.md` for feature documentation
- Examine API endpoints in `backend/api/` directory

Built for **National CyberShield Hackathon 2025** 🏆
