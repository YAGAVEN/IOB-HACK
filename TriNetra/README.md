# TriNetra - Financial Crime Detection
*Making the invisible visible*

TriNetra is an advanced, AI-powered financial crime detection platform designed to detect, visualize, and report suspicious activities seamlessly.

## Quick Start

The easiest way to get both the React frontend and Flask backend running locally is using the single startup script:

```bash
# Start both Backend & Frontend servers concurrently
./start.sh
```

**Access the Application:**
- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://localhost:5001](http://localhost:5001)

*Note: Press `Ctrl+C` in your terminal to shut down both processes safely.*

## Features

TriNetra modules are designed to tackle distinct phases of anti-money laundering and financial crime detection:

- 🕐 **CHRONOS**: Time-lapse transaction visualization using interactive graphs and node networks.
- � **Auto-SAR**: Generate and validate comprehensive, regulatory-compliant Suspicious Activity Reports (SARs) with one click using AI Analysis and Map visualizations.
- �🐍 **HYDRA**: AI red-teaming arena. Test detection models against adversarially generated synthetic transaction patterns.
- � **Mule Detection**: Identify potential money mules and account intermediaries by analyzing network relationships and velocity metrics.

## Tech Stack

The architecture has been unified for robustness and modern web performance:

- **Frontend:** React + Vite + Tailwind CSS + D3.js + Leaflet
- **Backend:** Python Flask
- **Database:** Supabase (PostgreSQL) + Fallback to SQLite (configurable via `.env`)

---
*Built for National CyberShield Hackathon 2025*