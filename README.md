# IOB-HACK: Advanced Network Visualization & Analysis Platform

## Overview

IOB-HACK is a comprehensive platform for real-time network visualization, analysis, and system diagnostics. It combines multiple advanced visualization modules to provide deep insights into complex system architectures and network topologies.

## Key Features

### 🌐 **Hydra Module**

- Interactive network topology visualization
- Real-time node and connection mapping
- Dynamic visualization with smooth animations
- Node clustering and relationship analysis

### ⏱️ **Chronos Module**

- Timeline-based event tracking and analysis
- Temporal data visualization
- Performance metrics over time
- Event correlation and pattern detection

### 🔧 **Autosar Module**

- Automotive Software Architecture visualization
- System component mapping
- Architectural relationships and dependencies
- Enhanced data representation

## Tech Stack

### Frontend

- **Framework**: Vite + JavaScript
- **Styling**: Tailwind CSS
- **Visualization**: Custom canvas-based rendering
- **WebSocket**: Real-time data streaming
- **Build**: Modern ES modules with hot reload

### Backend

- **Language**: Python
- **Framework**: Flask
- **APIs**: RESTful architecture
- **Data Processing**: Synthetic data generation and analysis

## Project Structure

```
IOB-HACK/
├── TriNetra/              # Main application
│   ├── frontend/          # Web UI (Vite + Tailwind)
│   │   ├── js/           # Core application logic
│   │   ├── css/          # Stylesheets
│   │   └── html/         # UI templates
│   └── backend/          # Python Flask backend
│       ├── api/          # API endpoints
│       ├── data/         # Data processing
│       └── models/       # Data models
└── [config files]        # Build and deployment configs
```

## Getting Started

### Prerequisites

- Node.js 16+
- Python 3.8+
- Modern web browser

### Installation

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd TriNetra/frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the application
./start.sh

# Or manually:
# Terminal 1: Backend
cd TriNetra/backend
python app.py

# Terminal 2: Frontend
cd TriNetra/frontend
npm run dev
```

## Configuration

- **Frontend**: See `TriNetra/frontend/vite.config.js`
- **Backend**: See `TriNetra/backend/config.py`
- **Deployment**: See `vercel.json` for Vercel deployment config

## Documentation

- [Hackathon Analysis Report](./Hackathon_Analysis_Report.md)
- [Technical Architecture](./VisuLaundNet_Technical_Architecture.md)
- [Setup Guide](./SETUP_GUIDE.md)

## Recent Enhancements

- ✅ WebSocket integration for real-time updates
- ✅ Tailwind CSS design system implementation
- ✅ Button visibility and UX improvements
- ✅ Network topology visualization fixes
- ✅ Chronos timeline animation enhancements
- ✅ Autosar module integration

## Build & Deployment

### Development

```bash
npm run dev
```

### Production Build

```bash
npm run build
```

### Deployment

Configured for Vercel. Push to main branch to deploy automatically.

## API Endpoints

- **Hydra API**: `/api/hydra` - Network topology data
- **Chronos API**: `/api/chronos` - Timeline events
- **Autosar API**: `/api/autosar` - Architecture data

## Contributing

To contribute to this project:

1. Create a feature branch
2. Commit your changes
3. Submit a pull request

## License

[Add your license information here]

## Support

For issues or questions, please refer to the documentation or create an issue in the repository.

---

**Last Updated**: February 2026
