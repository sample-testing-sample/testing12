# QuadraDiag + NeuroTract Integrated Platform
## Setup & Deployment Guide

### Platform Overview
This is a unified clinical intelligence platform combining:
- **Features 1-4**: Disease Risk Assessment (Diabetes, Heart, Liver, Parkinson's)
- **Feature 5**: Brain MRI Analysis (NeuroTract Integration)

### System Architecture
```
Frontend:
  - QuadraDiag UI (http://localhost:8000)
  - MRI Interface (embedded in Feature 5)

Backend:
  - QuadraDiag API (http://localhost:8000/api/v1)
  - NeuroTract API (http://localhost:8001)
```

### Prerequisites
- Python 3.11 or 3.13
- Node.js 18+ (for MRI frontend)
- 8GB RAM minimum (for MRI processing)

### Quick Start

#### Option 1: Automated Setup (Recommended)

**Windows:**
```powershell
.\setup.ps1
.\startup.ps1
```

**Linux/macOS:**
```bash
chmod +x setup.sh startup.sh
./setup.sh
./startup.sh
```

#### Option 2: Manual Setup

**Step 1: Setup QuadraDiag**
```bash
cd /workspaces/testing12
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

**Step 2: Setup NeuroTract**
```bash
cd MRI/Neurotract
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
cd src/frontend
npm install
cd ../..
```

**Step 3: Download MRI Dataset (Optional)**
```bash
# See DATASET_DOWNLOAD.md for instructions
```

**Step 4: Launch Services**
```bash
# Terminal 1: Main Platform
source .venv/bin/activate
python app.py

# Terminal 2: MRI Backend (from MRI/Neurotract)
source .venv/bin/activate
python -m uvicorn src.backend.api.server:app --host localhost --port 8001

# Terminal 3: MRI Frontend (from MRI/Neurotract/src/frontend)
npm run dev
```

### Accessing the Platform
- **Main Dashboard**: http://localhost:8000
- **MRI Analysis**: Click "MRI Analysis" button in navigation
- **API Docs**: http://localhost:8000/docs (QuadraDiag) or http://localhost:8001/docs (NeuroTract)

### Troubleshooting

**Port Already in Use:**
- Edit startup scripts to use alternative ports
- Update configuration in `quadra_diag/core/config.py`
- Update MRI API client settings

**Missing Dependencies:**
- Run `pip install --upgrade pip`
- Try `pip install -r requirements.txt --force-reinstall`

**MRI Frontend Not Loading:**
- Ensure Node.js is installed: `node --version`
- Verify npm packages: `npm install` in `MRI/Neurotract/src/frontend`
- Check browser console for errors

### Dataset Setup
See [DATASET_DOWNLOAD.md](DATASET_DOWNLOAD.md) for downloading and processing MRI data.

### Documentation
- [QuadraDiag README](README.md)
- [NeuroTract README](MRI/Neurotract/README.md)
- [Platform Architecture](PLATFORM_ARCHITECTURE.md)
