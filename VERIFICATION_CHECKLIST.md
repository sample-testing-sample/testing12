# Integration Verification Checklist

Use this checklist to verify that the QuadraDiag + NeuroTract integration is complete and working.

## Pre-Integration Requirements

- [x] Both projects extracted to correct locations
- [x] Python 3.11+ installed
- [x] Node.js 18+ installed (for MRI frontend)
- [x] Git available in terminal

## Integration Components

### Core Integration

- [x] MRI spec added to `quadra_diag/ml/catalog.py`
  - Contains: title, description, is_imaging_module flag, external_api URL
  
- [x] MRI routes created in `quadra_diag/web/routes.py`
  - GET `/mri` - MRI interface page
  - GET `/mri/proxy/{path:path}` - Proxy to NeuroTract API

- [x] MRI template created: `quadra_diag/web/templates/mri.html`
  - Status indicator for backend availability
  - NeuroTract interface iframe
  - Documentation panel
  
- [x] Navigation updated: `quadra_diag/web/templates/components/nav.html`
  - MRI Analysis button added with violet accent

- [x] Home page updated: `quadra_diag/web/templates/home.html`
  - Disease cards now support imaging modules
  - Feature count updated (4 → 5)
  - Platform metrics updated

- [x] Dependencies updated: `pyproject.toml`
  - Added `httpx>=0.28,<1.0` for HTTP proxying

### Automation & Scripts

- [x] Setup script created: `setup.sh` (Linux/macOS)
  - Activates Python 3.11+ check
  - Creates virtual environments
  - Installs dependencies
  - Initializes databases
  
- [x] Setup script created: `setup.ps1` (Windows PowerShell)
  - Python version validation
  - Environment setup with proper activation

- [x] Startup script created: `startup.sh` (Linux/macOS)
  - Starts QuadraDiag on 8000
  - Starts NeuroTract Backend on 8001
  - Starts NeuroTract Frontend on 3000
  - Displays service URLs

- [x] Startup script created: `startup.ps1` (Windows PowerShell)
  - Service startup with proper process tracking
  - Status information display

### Documentation

- [x] SETUP_GUIDE.md created
  - Platform overview
  - Quick start instructions (both Windows & Unix)
  - Troubleshooting guide

- [x] PLATFORM_ARCHITECTURE.md created
  - System design diagrams
  - Component descriptions
  - Data flow explanations
  - Technology stack summary
  - Security considerations
  - Scalability path

- [x] DATASET_DOWNLOAD.md created
  - Dataset sources (Stanford HARDI, HCP, OpenNeuro)
  - Dataset setup instructions
  - Quick start processing commands
  - Troubleshooting for data issues
  - Output file descriptions

- [x] QUICK_START.md created
  - Integration summary
  - 3-step quick start
  - Feature overview
  - Integration points explained
  - Testing procedures

## File Structure Verification

Verify these files and directories exist:

### QuadraDiag Files Modified/Created
```
✓ quadra_diag/ml/catalog.py          - MRI spec added
✓ quadra_diag/web/routes.py          - MRI routes added
✓ quadra_diag/web/templates/mri.html - NEW MRI template
✓ quadra_diag/web/templates/components/nav.html - Updated
✓ quadra_diag/web/templates/home.html - Updated
✓ pyproject.toml                     - Dependencies updated
```

### Root Level Files Created/Modified
```
✓ setup.sh                           - NEW Unix setup script
✓ setup.ps1                          - NEW Windows setup script
✓ startup.sh                         - NEW Unix startup script
✓ startup.ps1                        - NEW Windows startup script
✓ SETUP_GUIDE.md                     - NEW
✓ PLATFORM_ARCHITECTURE.md           - NEW
✓ DATASET_DOWNLOAD.md                - NEW
✓ QUICK_START.md                     - NEW
```

### NeuroTract Structure (Existing)
```
✓ MRI/Neurotract/src/backend/        - Backend API
✓ MRI/Neurotract/src/frontend/       - Next.js frontend
✓ MRI/Neurotract/datasets/           - Test data included
✓ MRI/Neurotract/requirements.txt    - Dependencies
```

## Functional Verification Steps

### 1. Code Quality Check

Run these commands to verify code structure:

```bash
# Verify Python syntax
python -m py_compile quadra_diag/ml/catalog.py quadra_diag/web/routes.py

# Check template syntax (if Jinja2 validation available)
# Files: quadra_diag/web/templates/mri.html, home.html, nav.html
```

### 2. Configuration Check

Verify all configuration is in place:

```bash
# Check MRI spec in catalog
grep -A 5 '"mri":' quadra_diag/ml/catalog.py

# Check MRI routes in web routes
grep -A 2 '@web_router.get("/mri")' quadra_diag/web/routes.py

# Check navigation has MRI button
grep -i "MRI Analysis" quadra_diag/web/templates/components/nav.html

# Check home page has 5 features
grep -i "5\|feature" quadra_diag/web/templates/home.html | head -5
```

### 3. Import Check

Verify imports are correct:

```bash
cd /workspaces/testing12

# Python: Check FastAPI routes load correctly
python -c "from quadra_diag.web.routes import web_router; print('Web routes loaded:', web_router)"

# Python: Check ML catalog loads
python -c "from quadra_diag.ml.catalog import DISEASE_SPECS; print('DISEASE_SPECS keys:', list(DISEASE_SPECS.keys()))"

# Python: Check httpx available
python -c "import httpx; print('httpx available:', httpx.__version__)"
```

### 4. Virtual Environment Check

Before running setup:

```bash
# Check if Python 3.11+ available
python --version

# Check if Node.js available (for MRI frontend)
node --version
npm --version

# Check project structure
ls -la MRI/Neurotract/src/backend/api/server.py
ls -la MRI/Neurotract/src/frontend/package.json
```

## Environment Setup Status

After running `./setup.sh`:

### QuadraDiag Environment
- [ ] Virtual environment created: `.venv/`
- [ ] Dependencies installed: `pip list` shows FastAPI, SQLAlchemy, SHAP, httpx, etc.
- [ ] Database initialized: `quadra_diag.db` exists
- [ ] Environment file: `.env` exists with configuration

### NeuroTract Environment
- [ ] Virtual environment created: `MRI/Neurotract/.venv/`
- [ ] Dependencies installed: nibabel, dipy, FastAPI, etc.
- [ ] Frontend dependencies: `MRI/Neurotract/src/frontend/node_modules/` exists
- [ ] Test data present: `MRI/Neurotract/datasets/Stanford dataset/` files exist

## Runtime Verification

After running `./startup.sh`, verify:

### Port Availability
- [ ] Port 8000 available (QuadraDiag)
- [ ] Port 8001 available (NeuroTract Backend)
- [ ] Port 3000 available (NeuroTract Frontend, optional)

### Service Health
- [ ] QuadraDiag accessible: http://localhost:8000
- [ ] NeuroTract API accessible: http://localhost:8001/docs
- [ ] Can view Swagger documentation at both backends

### Frontend Functionality
- [ ] Home page loads with 5 feature cards
- [ ] Can register/login successfully
- [ ] Navigation shows "MRI Analysis" button (after login)
- [ ] Can access each disease assessment form
- [ ] Dashboard displays without errors

### MRI Module
- [ ] `/mri` route responds (after login)
- [ ] Status indicator shows backend status
- [ ] "Open NeuroTract Interface" button functional
- [ ] Documentation displays correctly
- [ ] Can view Swagger API docs

## Database Verification

After setup, verify database:

```bash
# Check SQLite database created
file quadra_diag.db

# Verify tables created (Python)
python -c "
from quadra_diag.db.session import session_scope
from quadra_diag.db.models import User, PredictionRecord
with session_scope() as session:
    print('Tables initialized successfully')
"
```

## Documentation Verification

Verify all documentation files:

- [ ] SETUP_GUIDE.md - Complete setup instructions
- [ ] QUICK_START.md - Quick start guide
- [ ] PLATFORM_ARCHITECTURE.md - System design
- [ ] DATASET_DOWNLOAD.md - MRI data setup
- [ ] README.md - Original QuadraDiag docs (unchanged)
- [ ] MRI/Neurotract/README.md - NeuroTract docs (unchanged)

## Data Processing Readiness

Verify MRI data processing setup:

```bash
cd MRI/Neurotract

# Verify dataset files present
ls datasets/Stanford\ dataset/

# Verify output directory can be created
mkdir -p output/test

# Verify CLI works
python -m src.backend.cli --version
```

## Troubleshooting Checklist

If issues occur, verify:

- [ ] Python version: `python --version` shows 3.11+
- [ ] Virtual environment activated: `which python` shows `.venv` path
- [ ] Required files not corrupted: `python -m py_compile` succeeds
- [ ] Dependencies installed: `pip list` shows all required packages
- [ ] Ports not in use: `netstat -an | grep LISTEN` (check 8000, 8001, 3000)
- [ ] File permissions: Scripts are executable: `ls -l setup.sh startup.sh`
- [ ] Database accessible: Can write to project directory
- [ ] Network connectivity: Can reach localhost:port numbers

## Performance Baselines

Expected startup times:

- QuadraDiag Backend: 2-3 seconds
- NeuroTract Backend: 2-3 seconds
- NeuroTract Frontend: 3-5 seconds
- Total platform: 10-15 seconds to full availability

Expected response times:

- Home page load: <500ms
- Disease assessment: <100ms (prediction only, no SHAP)
- SHAP explanation: 500-2000ms (backend-intensive)
- MRI status check: 100-500ms
- API health check: <50ms

## Sign-Off

Integration verification complete when all boxes are checked:

- [ ] All files modified/created as documented
- [ ] Code compiles without errors
- [ ] All imports load successfully
- [ ] Setup scripts execute without errors
- [ ] Services start on correct ports
- [ ] Frontend displays correctly
- [ ] MRI module accessible after login
- [ ] Documentation complete and accurate

---

**Verification Date:** _______________
**Verified By:** _______________
**Status:** ✓ Complete / ⚠ Partial / ✗ Incomplete

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________

