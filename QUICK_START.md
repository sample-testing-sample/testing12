# QuadraDiag + NeuroTract Integration: Quick Start Guide

## What We've Done

The two projects have been successfully integrated into a unified medical intelligence platform:

### Integration Summary

✅ **MRI Added as 5th Feature**
- New module in `quadra_diag/ml/catalog.py`
- `is_imaging_module: True` flag for special handling
- Violet accent color for distinction from disease assessments

✅ **Web Interface Enhanced**
- New MRI navigation button (`/mri` route)
- MRI interface template with documentation
- Features listed on home page with new feature count (5 → updated)
- Proxy endpoint for communication between services

✅ **API Integration**
- MRI proxy route: `/mri/proxy/{path}`
- Direct routing to NeuroTract API on port 8001
- No blocking between services

✅ **Startup Infrastructure**
- `setup.sh` - Automated environment setup (Linux/macOS)
- `setup.ps1` - Automated environment setup (Windows)
- `startup.sh` - Unified startup script (Linux/macOS)
- `startup.ps1` - Unified startup script (Windows)

✅ **Documentation Created**
- `SETUP_GUIDE.md` - Setup instructions
- `PLATFORM_ARCHITECTURE.md` - System design
- `DATASET_DOWNLOAD.md` - MRI data processing guide

## Quick Start (3 Steps)

### Step 1: Prepare Environments

**Linux/macOS:**
```bash
cd /workspaces/testing12
chmod +x setup.sh startup.sh
./setup.sh
```

**Windows (PowerShell):**
```powershell
cd C:\path\to\project
.\setup.ps1
```

Expected output:
```
🏥 QuadraDiag + NeuroTract Setup
==================================
✓ Python 3.13 detected
✓ Virtual environment created
✓ Dependencies installed
...
✅ Setup Complete!
```

### Step 2: Start the Platform

**Linux/macOS:**
```bash
./startup.sh
```

**Windows (PowerShell):**
```powershell
.\startup.ps1
```

Expected services:
- ✓ Main Platform → http://localhost:8000
- ✓ NeuroTract Backend → http://localhost:8001
- ✓ NeuroTract Frontend → http://localhost:3000 (optional)

### Step 3: Access the Integrated System

1. **Open Browser:** http://localhost:8000
2. **Login/Register** as a new user
3. **Navigate to:** Dashboard → Look for "MRI Analysis" button
4. **Click MRI Analysis** to access the NeuroTract interface

## Platform Features (By Feature Module)

### Feature 1: Diabetes Risk Assessment
- 8 metabolic parameters
- Glucose, BMI, age-based predictions
- SHAP explanations
- CSV batch processing

### Feature 2: Heart Disease Risk Assessment
- 13 cardiovascular indicators
- ECG and blood pressure analysis
- Interactive risk visualization
- PDF report generation

### Feature 3: Liver Disease Risk Assessment
- 10 hepatic markers
- Enzyme and bilirubin analysis
- Batch lab result processing
- Excel export capability

### Feature 4: Parkinson's Risk Assessment
- 22 acoustic voice features
- MDVP and shimmer analysis
- Speech-based screening
- Clinical PDF reports

### Feature 5: MRI Analysis ✨ (NEW)
- 7-stage processing pipeline
- Brain connectivity analysis
- White matter tractography
- 3D interactive visualization
- Graph-theoretic metrics

## File Structure After Integration

```
/workspaces/testing12/
├── SETUP_GUIDE.md                    # Setup instructions
├── PLATFORM_ARCHITECTURE.md          # System design
├── DATASET_DOWNLOAD.md               # MRI data guide
├── setup.sh & setup.ps1              # Setup automation
├── startup.sh & startup.ps1          # Startup automation
│
├── quadra_diag/                      # Main platform (UPDATED)
│   ├── ml/
│   │   └── catalog.py               # ✓ Added MRI spec
│   ├── web/
│   │   ├── routes.py                # ✓ Added /mri routes
│   │   └── templates/
│   │       ├── mri.html             # ✓ NEW MRI interface
│   │       ├── components/
│   │       │   └── nav.html         # ✓ Added MRI button
│   │       └── home.html            # ✓ Updated for 5 features
│   └── ... (other existing modules)
│
├── MRI/
│   └── Neurotract/                  # NeuroTract (READY)
│       ├── src/backend/api/
│       │   └── server.py            # FastAPI (CORS enabled)
│       ├── src/frontend/            # Next.js frontend
│       ├── datasets/
│       │   └── Stanford dataset/    # Test data included
│       └── output/                  # Processing results
│
├── models/
│   ├── diabetes.joblib
│   ├── heart.joblib
│   ├── liver.joblib
│   └── parkinsons.joblib
│
└── requirements.txt                 # ✓ Updated with httpx
```

## Key Integration Points

### 1. MRI Feature in Catalog
File: `quadra_diag/ml/catalog.py`
```python
"mri": {
    "title": "MRI Analysis",
    "description": "Advanced brain connectivity and white matter analysis using NeuroTract.",
    "is_imaging_module": True,
    "external_api": "http://localhost:8001",
    ...
}
```

### 2. Navigation Integration
File: `quadra_diag/web/templates/components/nav.html`
```html
<a href="/mri" {% if request.url.path == '/mri' %}aria-current="page"{% endif %} 
   class="button button-small button-accent">MRI Analysis</a>
```

### 3. MRI Routes
File: `quadra_diag/web/routes.py`
```python
@web_router.get("/mri")
async def mri_interface(request: Request):
    # Returns MRI interface with NeuroTract integration
    
@web_router.get("/mri/proxy/{path:path}")
async def mri_proxy(request: Request, path: str):
    # Proxies requests to NeuroTract API
```

### 4. Home Page Update
File: `quadra_diag/web/templates/home.html`
```jinja2
{% if disease.is_imaging_module %}
  {# Special handling for MRI #}
  <a href="/mri" class="button button-primary">Access NeuroTract →</a>
{% endif %}
```

## Environment Variables

### QuadraDiag (.env)
```
APP_NAME=QuadraDiag
APP_ENV=development
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./quadra_diag.db
SECRET_KEY=your-secret-key-here
NEUROTRACT_API=http://localhost:8001
```

### NeuroTract (MRI/Neurotract .env)
```
LOG_LEVEL=INFO
UPLOAD_DIR=uploads
OUTPUT_DIR=output
```

## Testing the Integration

### 1. Verify Backend Connectivity
```bash
# Check QuadraDiag API
curl http://localhost:8000/api/v1/health

# Check NeuroTract API
curl http://localhost:8001/docs
```

### 2. Test Disease Assessments
1. Navigate to http://localhost:8000
2. Click "Start Assessment" on any disease card
3. Fill in parameters and submit
4. View results with SHAP explanations

### 3. Test MRI Module
1. Go to http://localhost:8000/dashboard
2. Click "MRI Analysis" button
3. Verify:
   - Status indicator shows "Online" (if backend running)
   - "Open NeuroTract Interface" button works
   - Documentation loads correctly

### 4. Test Data Processing
```bash
cd MRI/Neurotract
source .venv/bin/activate

# Process included Stanford dataset
python -m src.backend.cli preprocess \
  --input "datasets/Stanford dataset/SUB1_b1000_1.nii.gz" \
  --bvals "datasets/Stanford dataset/SUB1_b1000_1.bvals" \
  --bvecs "datasets/Stanford dataset/SUB1_b1000_1.bvecs" \
  --output "output/SUB1/preprocessed" \
  --no-motion-correction
```

## Architecture Diagram

```
UNIFIED PLATFORM (http://localhost:8000)
│
├─ Disease Assessments (Features 1-4) ─┐
│  ├─ Diabetes                         │
│  ├─ Heart                            │
│  ├─ Liver                            │
│  └─ Parkinson's                      │
│                                      ├─ Auth
├─ Analytics & Dashboards              │  ├─ Report Gen
│  ├─ Trends                           │  ├─ PDF Export
│  ├─ Comparisons                      │  └─ Data Export
│  └─ Admin                            │
│                                      μ─ FastAPI
└─ MRI Analysis (Feature 5) ──────────┘  Backend
   │
   └─ /mri route
      ├─ Interface Template
      ├─ /mri/proxy endpoint
      │
      └─ NeuroTract Backend (8001)
         ├─ Job Management
         ├─ Processing Pipeline
         └─ Result Storage
         
         ├─ NeuroTract Frontend (3000)
         │  ├─ 3D Visualization
         │  ├─ Data Upload
         │  └─ Results View
         │
         └─ Shared Processing
            ├─ output/
            ├─ datasets/
            └── logs/
```

## Next Steps

### 1. Setup (First Time Only)
```bash
./setup.sh       # or setup.ps1 on Windows
```

### 2. Start Services
```bash
./startup.sh     # or startup.ps1 on Windows
```

### 3. Download MRI Data (Optional)
See `DATASET_DOWNLOAD.md` for instructions on:
- Using included Stanford dataset
- Downloading HCP data
- Using OpenNeuro datasets
- Processing custom data

### 4. Deploy to Production
See `PLATFORM_ARCHITECTURE.md` for:
- Security hardening
- HTTPS setup
- Docker containerization
- Kubernetes deployment

## Troubleshooting

### Services won't start
- Check ports 8000, 8001, 3000 are available
- Verify Python 3.11+ installed
- Check virtual environments activated properly
- Review logs in console output

### MRI module shows "Offline"
- Verify NeuroTract Backend started on port 8001
- Check firewall settings
- Try http://localhost:8001/docs in browser

### Database errors
- Delete `quadra_diag.db` to reset
- Run: `python -c "from quadra_diag.db.session import init_db; init_db()"`

### Import errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Check virtual environment activated: `which python` should show .venv path

## Documentation Files

- **SETUP_GUIDE.md** - Detailed setup for different environments
- **PLATFORM_ARCHITECTURE.md** - System design and deployment options
- **DATASET_DOWNLOAD.md** - MRI data sources and processing
- **README.md** - Original QuadraDiag documentation
- **MRI/Neurotract/README.md** - NeuroTract documentation

## Support & Development

### Development Mode
- FastAPI auto-reloads on file changes (add `--reload` to uvicorn)
- Next.js auto-reloads with `npm run dev`
- Database auto-initializes on startup

### Adding New Features
1. Add to `DISEASE_SPECS` in `quadra_diag/ml/catalog.py`
2. Create route in `quadra_diag/web/routes.py`
3. Create template in `quadra_diag/web/templates/`
4. Train ML model in `scripts/train_models.py`

### Extending MRI Integration
1. Add new endpoints to NeuroTract backend
2. Update proxy routes in QuadraDiag
3. Add UI controls to `mri.html` template
4. Update documentation

## License & Attribution

- **QuadraDiag:** Built by Riddhima and Sakshi
- **NeuroTract:** Brain Tractography and Connectivity Analysis
- **DIPY:** Diffusion Imaging in Python
- **nibabel:** NIfTI tools library

---

✅ **Integration Complete!**

Your unified medical intelligence platform is ready. Start with:
```bash
./setup.sh && ./startup.sh
```

Then open: **http://localhost:8000**

