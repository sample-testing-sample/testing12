# Platform Architecture: QuadraDiag + NeuroTract Integration

## System Overview

The integrated platform combines two complementary clinical intelligence systems:

```
┌─────────────────────────────────────────────────────────────────┐
│                    QuadraDiag v3.0 Frontend                       │
│              http://localhost:8000 (Main Interface)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   Disease Risk   │  │  Analytics &     │  │  5th Feature:    │ │
│  │  Assessments     │  │  Dashboards      │  │  MRI Analysis    │ │
│  │  (4 modules)     │  │  (Trends, Comp)  │  │  (NEW)           │ │
│  └┬─────────────────┘  └─────────────────┬┘  └┬──────────────────┘ │
│   │                                      │    │                   │
│   └──────────┬───────────────────────────┴────┴─────────────────┘ │
│              │                                                   │
│     Jinja2 Templates + Vanilla JS + Chart.js                    │
└──────────────┼───────────────────────────────────────────────────┘
               │
          ┌────┴────┐
          │          │
    ┌─────▼────┐  ┌─▼──────────────┐
    │QuadraDiag│  │NeuroTract Proxy│
    │ Backend  │  │   (/mri/proxy) │
    │  (8000)  │  └┬────────────────┘
    └─────┬────┘   │
          │        │
          │   ┌────▼──────────────────┐
          │   │NeuroTract Backend API │
          │   │    (8001)             │
    ┌─────▼───┼───┬───────────────────┘
    │          │   │
  ┌─┴──────┐  │   │   ┌──────────────────────┐
  │SQLite  │  │   └──▶│NeuroTract Frontend   │
  │Models  │  │       │ (Next.js - 3000)     │
  │Cache   │  │       │ (Embedded in MRI tab)│
  │DB      │  │       └──────────────────────┘
  └────────┘  │
              │
    ┌─────────▼─────────────────┐
    │   Unified Service Layer    │
    ├────────────────────────────┤
    │• Authentication            │
    │• Session Management        │
    │• Data Export               │
    │• Multi-service Routing     │
    └────────────────────────────┘
```

## Component Architecture

### 1. Frontend Layer (Port 8000)

**QuadraDiag Web Interface**
- **Framework:** Jinja2 templates + Vanilla JavaScript
- **Styling:** CSS3 with dark mode support
- **Charting:** Chart.js for analytics
- **Authentication:** Session-based with PBKDF2 password hashing

**Features:**
- Disease risk assessment forms (4 modules)
- Interactive dashboards with real-time analytics
- Report generation and export
- User profile and settings management
- Admin panel for platform metrics
- **NEW:** MRI Analysis module (5th feature)

**MRI Integration:**
- Dedicated `/mri` route and `mri.html` template
- Embedded NeuroTract interface iframe
- Status monitoring for backend availability
- Documentation and quick-start guides

### 2. Backend Layer

#### QuadraDiag Backend (Port 8000)
**Framework:** FastAPI + Uvicorn
**Database:** SQLite with SQLAlchemy 2.0 ORM

**Key Modules:**
```
quadra_diag/
├── api/
│   └── routes.py              # REST API endpoints
├── web/
│   ├── routes.py              # Web routes (NEW: /mri routes)
│   └── templates/
│       └── mri.html           # MRI interface template (NEW)
├── ml/
│   ├── catalog.py             # Disease specs (NEW: mri spec)
│   ├── training.py            # Model management
│   └── models/                # ML models
├── services/
│   ├── prediction.py          # Disease risk scoring
│   ├── explainability.py      # SHAP explanations
│   ├── pdf_generator.py       # Report generation
│   ├── analytics.py           # Trend analysis
│   └── reporting.py           # Batch processing
├── db/
│   ├── models.py              # SQLAlchemy ORM models
│   └── session.py             # Database session management
└── core/
    ├── config.py              # Configuration management
    ├── logging.py             # Logging setup
    ├── cache.py               # TTL cache for metrics
    └── middleware.py          # Request middleware stack
```

**API Endpoints:**
- `/api/v1/health` - Health check
- `/api/v1/predict/{disease}` - Single prediction
- `/api/v1/batch-process` - Batch predictions
- `/mri` - MRI interface page
- `/mri/proxy/{path}` - Proxy to NeuroTract API

#### NeuroTract Backend (Port 8001)
**Framework:** FastAPI + Uvicorn
**Language:** Python with scientific computing stack

**Key Features:**
- 7-stage MRI processing pipeline
- Tractography and connectome analysis
- Graph-theoretic metrics computation
- Async job management with file-based persistence

**Processing Pipeline:**
1. **Preprocessing** - Motion/eddy correction, brain extraction, bias field correction
2. **DTI** - Fractional Anisotropy, Mean Diffusivity computation
3. **CSD** - Fiber orientation distribution estimation
4. **Tractography** - Probabilistic fiber tracking
5. **Surfaces** - Brain mesh and parcellation mapping
6. **Connectome** - Structural connectivity matrix construction
7. **Metrics** - Network graph analysis

### 3. Database Layer

**QuadraDiag (SQLite)**
```sql
Users
  ├── id, username, email, password_hash
  └── role (patient, clinician, admin)

PredictionRecords
  ├── id, user_id, disease, probability, risk_band
  ├── submitted_features, shap_values, feature_importance
  └── timestamp

UploadReports
  ├── id, user_id, file_data, processed
  └── timestamps
```

**NeuroTract (File-based)**
- Job database: `jobs_database.json`
- Output directory: `output/{subject_id}/`
- Result cache: `.cache/`

### 4. Integration Points

#### HTTP Proxying
- QuadraDiag provides `/mri/proxy/{path}` endpoint
- Proxies requests to NeuroTract API on port 8001
- Handles authentication and error management

#### Direct Communication
- NeuroTract frontend can be embedded via iframe
- Direct API calls from MRI interface to port 8001
- Sharing session context between applications

#### File Sharing
- Both systems can read/write to shared `output/` directory
- Processed MRI results accessible to QuadraDiag
- Batch reports can reference NeuroTract outputs

## Data Flow

### Disease Risk Assessment Flow
```
User Input → Form Validation → Feature Scaling → 
ML Model Prediction → SHAP Explanation → 
Result Visualization → Database Storage → PDF Generation
```

### MRI Analysis Flow
```
Patient Data (NIfTI) → 
  ├─ Sent to NeuroTract Backend
  ├─ Processing Pipeline (7 stages)
  └─ Results stored in output/

Results → 
  ├─ Viewed in NeuroTract Frontend
  ├─ Via MRI Tab in QuadraDiag
  └─ Accessed through unified API
```

## Deployment Architecture

### Single Machine Deployment
```
Machine (localhost)
├── Port 8000: QuadraDiag (Main Platform)
├── Port 8001: NeuroTract Backend (API)
├── Port 3000: NeuroTract Frontend (Next.js)
├── SQLite: QuadraDiag Database
└── File System: Shared Outputs
```

### Virtual Environment Isolation
```
Project Root (.venv)
├── quadra_diag dependencies
├── FastAPI 0.115+
├── SQLAlchemy 2.0
├── SHAP, scikit-learn, pandas
└── Additional (httpx for proxying)

MRI/Neurotract (.venv)
├── dipy, nibabel, nilearn
├── FastAPI 0.100+
├── networkx, trimesh, fury
└── Scientific Computing Stack
```

## Authentication & Authorization

### QuadraDiag
- Session-based authentication
- PBKDF2 password hashing
- Role-based access control (Patient, Clinician, Admin)
- MRI module requires authentication

### NeuroTract
- Currently open API (CORS enabled for *)
- Future: Token-based authorization
- Job ownership tracking via user context

## Performance Considerations

### QuadraDiag
- In-memory TTL cache for platform metrics (60s)
- Vectorized NumPy operations for batch processing
- Lazy loading of SHAP explanations
- Gzip compression for responses

### NeuroTract
- Async job processing with background tasks
- Streaming responses for large files
- Multi-threaded tractography algorithms
- Memory-efficient nibabel streaming for NIfTI files

### Integration
- No blocking between services
- Asynchronous proxy requests
- Independent scaling capability

## Scalability Path

### Phase 1: Current Setup
- Single machine, both applications
- Suitable for development and testing
- 10-50 concurrent users

### Phase 2: Separate Backends
- Deploy NeuroTract on dedicated GPU machine
- QuadraDiag on separate CPU machine
- Use docker-compose for orchestration

### Phase 3: Microservices
- ML inference service (separate predictions)
- Background job workers (celery/redis)
- Load balancer (nginx)
- Cache layer (redis)
- Database replication

### Phase 4: Kubernetes
- Container orchestration
- Auto-scaling based on load
- Service mesh for communication
- Persistent volumes for data

## Security Considerations

### Current Implementation
- ✅ HTTPS not enforced (development)
- ✅ PBKDF2 password hashing
- ✅ Session-based authentication
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ⚠️ CORS open to all origins (development)
- ⚠️ No rate limiting

### Production Recommendations
1. Enable HTTPS/TLS
2. Restrict CORS origins
3. Implement rate limiting (API Key, IP-based)
4. Add request signing for inter-service communication
5. Use environment variables for secrets
6. Implement audit logging
7. Add role-based access control to NeuroTract
8. Use OAuth2 for multi-user scenarios

## Technology Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend (Web) | Jinja2 + Vanilla JS | Python 3.11+ |
| Frontend (MRI) | Next.js + Three.js | Node 18+ |
| Backend (Main) | FastAPI | 0.115+ |
| Backend (MRI) | FastAPI | 0.100+ |
| ML Framework | scikit-learn | 1.6+ |
| Explainability | SHAP | 0.45+ |
| Medical Imaging | DIPY, nibabel | Latest |
| Graphics | Three.js | 3.0+ |
| Database | SQLite | 3.36+ |

## File Structure

```
/workspaces/testing12/
├── SETUP_GUIDE.md              # Setup instructions
├── DATASET_DOWNLOAD.md         # MRI data setup
├── PLATFORM_ARCHITECTURE.md    # This file
├── setup.sh / setup.ps1        # Automated setup scripts
├── startup.sh / startup.ps1    # Unified startup scripts
│
├── quadra_diag/                # Main platform
├── app.py                       # Main entry point
├── requirements.txt             # Main dependencies
│
├── MRI/
│   └── Neurotract/             # NeuroTract MRI platform
│       ├── src/backend/        # Backend API
│       ├── src/frontend/       # Next.js frontend
│       ├── datasets/           # MRI data directory
│       ├── output/             # Processing outputs
│       └── requirements.txt    # MRI dependencies
│
└── models/                      # Pre-trained ML models
    ├── diabetes.joblib
    ├── heart.joblib
    ├── liver.joblib
    └── parkinsons.joblib
```

## Environment Configuration

### Main Application (.env)
```
APP_NAME=QuadraDiag
APP_ENV=development
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./quadra_diag.db
SECRET_KEY=your-secret-key
NEUROTRACT_API=http://localhost:8001
```

### MRI Setup (.env in MRI/Neurotract)
```
LOG_LEVEL=INFO
UPLOAD_DIR=uploads
OUTPUT_DIR=output
CORS_ORIGINS=["http://localhost:8000", "http://localhost:3000"]
```

## Startup Sequence

1. **Unified startup script** (`startup.sh` or `startup.ps1`)
2. **QuadraDiag Backend** (Port 8000, ~2s startup)
3. **NeuroTract Backend** (Port 8001, ~2s startup)
4. **NeuroTract Frontend** (Port 3000, ~3s startup)
5. **Ready for access** (http://localhost:8000)

## Accessing the Platform

### User Interface
- **Main Dashboard:** http://localhost:8000
- **MRI Analysis:** http://localhost:8000/mri (after login)
- **NeuroTract Direct:** http://localhost:3000 (optional)
- **Admin Panel:** http://localhost:8000/admin

### API Documentation
- **Main API:** http://localhost:8000/docs (Swagger UI)
- **MRI API:** http://localhost:8001/docs (Swagger UI)

### Data & Results
- **MRI Outputs:** `MRI/Neurotract/output/`
- **Reports:** `./reports/` and `./pdfs/`
- **Database:** `./quadra_diag.db` (SQLite)

## Development Workflow

1. **Code Changes:**
   - FastAPI auto-reloads with `--reload` flag
   - Frontend hot-reloads with `npm run dev`

2. **Testing:**
   ```bash
   cd /workspaces/testing12
   pytest tests/
   ```

3. **Database Migrations:**
   ```bash
   # Manual migration (SQLAlchemy handles auto-creation)
   python -c "from quadra_diag.db.session import init_db; init_db()"
   ```

4. **Model Updates:**
   - Retrain in `scripts/train_models.py`
   - Update joblib files in `models/`

## Monitoring & Logging

### QuadraDiag
- Logs to console and `./logs/`
- Log level: DEBUG (dev) → INFO (prod)
- Metrics available at `/api/v1/health`

### NeuroTract
- Logs to console and `MRI/Neurotract/logs/`
- Per-job logging in `output/{subject}/logs/`
- Status available at `/docs` endpoint

---

**v1.0** | Updated: 2026-04-27 | Integration complete ✓
