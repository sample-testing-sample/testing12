# QuadraDiag v3.0

**Production-grade multi-disease clinical intelligence platform.**

Built by **Riddhima** and **Sakshi**.

---

## Overview

QuadraDiag is an advanced full-stack disease risk assessment platform for diabetes, heart disease, liver disease, and Parkinson's disease. It features validated ML models, SHAP explainability, batch CSV processing, interactive analytics, role-based access control, PDF/Excel export, dark mode, and a premium responsive UI.

## Features

### Clinical Workflows
- **Diabetes Risk Assessment** — Metabolic screening with 8 validated fields
- **Heart Disease Risk Assessment** — Cardiovascular screening with 13 fields
- **Liver Disease Risk Assessment** — Hepatic screening with 10 fields
- **Parkinson's Risk Assessment** — Neurological voice analysis with 22 fields
- **Probability output, risk bands (low/moderate/high), benchmark notes**

### Advanced Capabilities
- **SHAP Explainability** — Feature contribution visualization
- **Batch CSV Upload Lab** — Cohort screening with enriched reports
- **PDF Report Generation** — Professional clinical PDF downloads
- **Excel Export** — `.xlsx` batch report downloads
- **Interactive Analytics** — Chart.js dashboards with trends, distributions
- **Assessment Comparison** — Side-by-side comparison of historical assessments
- **Data Export** — JSON export of all user data

### User Management
- **Role-Based Access** — Patient, Clinician, Admin roles
- **Password Strength Validation** — 8+ chars, uppercase, lowercase, digit, special char
- **Password Change** — Secure in-app password update
- **Session-Based Authentication** — Persistent prediction history
- **Admin Dashboard** — Platform metrics, user management, recent activity

### Engineering
- **Modular FastAPI** — Reusable schemas, separated API/web/ML/service layers
- **Middleware Stack** — Request ID, timing, GZip, CORS, security headers, trusted hosts
- **TTL Cache** — In-memory caching for platform metrics
- **Graceful Degradation** — SHAP, PDF, Excel fallbacks if dependencies missing
- **Dark Mode** — System preference detection + manual toggle with persistence
- **Responsive Design** — Mobile-first with animated navigation
- **Comprehensive Tests** — 21 tests covering all features

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2 |
| ML | scikit-learn, pandas, NumPy, joblib, SHAP (optional) |
| Frontend | Jinja2, CSS3, Vanilla JS, Chart.js |
| Database | SQLite (configurable) |
| Testing | pytest, FastAPI TestClient |
| Export | reportlab (PDF), openpyxl (Excel) |

## Quick Start

### Python 3.11

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python app.py
```

### Python 3.13

```powershell
py -3.13 -m venv .venv313
.\.venv313\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python app.py
```

## Endpoints

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Homepage |
| `http://127.0.0.1:8000/dashboard` | User dashboard |
| `http://127.0.0.1:8000/analytics` | Interactive analytics |
| `http://127.0.0.1:8000/compare` | Assessment comparison |
| `http://127.0.0.1:8000/profile` | User profile & password change |
| `http://127.0.0.1:8000/settings` | Preferences & data export |
| `http://127.0.0.1:8000/admin` | Admin dashboard |
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc API docs |

## API Examples

### Health Check
```powershell
curl http://127.0.0.1:8000/api/v1/health
```

### Single Prediction
```powershell
curl -X POST http://127.0.0.1:8000/api/v1/predict/diabetes `
  -H "Content-Type: application/json" `
  -d "{\"Pregnancies\":2,\"Glucose\":135,\"BloodPressure\":70,\"SkinThickness\":20,\"Insulin\":85,\"BMI\":31.2,\"DiabetesPedigreeFunction\":0.45,\"Age\":42}"
```

### Batch CSV Prediction
```powershell
curl -X POST http://127.0.0.1:8000/api/v1/predict/diabetes/batch `
  -F "file=@diabetes_batch.csv"
```

## Tests

```powershell
python -m pytest
```

21 comprehensive tests covering:
- Homepage rendering
- Health endpoint
- All 4 disease prediction APIs
- Dynamic prediction API
- Invalid disease/payload handling
- 404 pages
- Registration & login flows
- Weak password rejection
- Duplicate registration prevention
- Dashboard access control
- Profile & password change
- Analytics & comparison access control
- Settings access control
- Batch upload (web + API)
- Batch upload login requirements
- Template downloads
- Disease form pages
- Assessment endpoint
- Invalid data handling
- Admin access control
- Dark mode toggle
- Analytics APIs
- System metrics API
- Data export
- Logout session clearing
- Correct liver feature labels

## Retrain Models

```powershell
python scripts/train_models.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application title | `QuadraDiag` |
| `APP_ENV` | Environment name | `development` |
| `SECRET_KEY` | Session signing key | `change-me-in-production` |
| `DATABASE_URL` | Database connection | `sqlite:///./runtime/quadra_diag.db` |
| `MODEL_DIR` | Trained model directory | `./models` |
| `DATASET_DIR` | Dataset directory | `./Dataset` |
| `MEDIA_DIR` | Static media directory | `./static` |
| `MODEL_AUTO_TRAIN` | Train models if missing | `true` |
| `LOG_LEVEL` | Log level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |
| `MAX_UPLOAD_SIZE_MB` | Max upload size | `10` |
| `MAX_BATCH_ROWS` | Max batch rows | `10000` |
| `METRICS_CACHE_TTL` | Metrics cache TTL (seconds) | `60` |
| `ENABLE_SHAP` | Enable SHAP explainability | `true` |
| `ENABLE_PDF_EXPORT` | Enable PDF generation | `true` |
| `ENABLE_EXCEL_EXPORT` | Enable Excel export | `true` |
| `ADMIN_EMAIL` | Default admin email | `admin@quadradiag.local` |

## Folder Structure

```
Quadra-Diag/
├── app.py                          # Entry point
├── pyproject.toml                  # Dependencies & project metadata
├── requirements.txt                # Pip requirements
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── Dataset/                        # Training datasets
├── models/                         # Trained models + metadata
├── scripts/
│   └── train_models.py             # Model training script
├── quadra_diag/
│   ├── main.py                     # FastAPI app factory
│   ├── schemas.py                  # Pydantic models
│   ├── api/
│   │   └── routes.py               # REST API endpoints
│   ├── core/
│   │   ├── config.py               # Settings
│   │   ├── logging.py              # Logging config
│   │   ├── middleware.py           # Middleware stack
│   │   └── cache.py                # TTL cache utility
│   ├── db/
│   │   ├── models.py               # SQLAlchemy models
│   │   └── session.py              # DB session management
│   ├── ml/
│   │   ├── catalog.py              # Disease specifications
│   │   └── training.py             # Model training pipeline
│   ├── services/
│   │   ├── auth.py                 # Password hashing/validation
│   │   ├── prediction.py           # ML inference
│   │   ├── reporting.py            # Batch processing
│   │   ├── explainability.py       # SHAP explanations
│   │   ├── pdf_generator.py        # PDF report generation
│   │   └── analytics.py            # Analytics engine
│   └── web/
│       ├── flash.py                # Flash messages
│       ├── routes.py               # Web routes
│       ├── static/
│       │   ├── styles.css          # All styles
│       │   └── app.js              # All JS
│       └── templates/
│           ├── base.html
│           ├── home.html
│           ├── dashboard.html
│           ├── analytics.html
│           ├── compare.html
│           ├── profile.html
│           ├── settings.html
│           ├── admin.html
│           ├── auth.html
│           ├── disease_form.html
│           ├── result.html
│           ├── assessment_detail.html
│           ├── report_detail.html
│           ├── 404.html
│           └── components/
│               ├── nav.html
│               ├── footer.html
│               ├── team_card.html
│               └── toasts.html
├── static/                         # Media assets (images)
├── tests/
│   ├── conftest.py                 # Test fixtures
│   └── test_app.py                 # 21 comprehensive tests
└── runtime/                        # DB + generated reports
```

## Critical Fixes in v3.0

1. **Loader Freezing** — Rewrote with timeout fallback, `pageshow` event, CSS transitions
2. **Liver Disease Labels** — Corrected all 10 clinical field labels
3. **Broken vercel.json** — Removed obsolete static HTML references
4. **Platform Metrics Performance** — Added TTL cache to eliminate redundant DB queries
5. **Password Security** — Added strength validation with clear error messages
6. **Session Security** — Production middleware with security headers, trusted hosts

## Notes

- This platform is for **educational screening and decision-support demonstrations only**
- Predictions are **not medical diagnoses**
- The first startup may take longer if models need to be generated
- Tested on Python 3.11.9 and 3.13.6

---

**Created by Riddhima and Sakshi**

