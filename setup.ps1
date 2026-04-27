# QuadraDiag + NeuroTract Unified Setup Script (Windows PowerShell)
# This script sets up both projects with their dependencies

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PYTHON_VERSION_REQUIRED = "3.11"

Write-Host "`n🏥 QuadraDiag + NeuroTract Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Function to check Python version
function Check-Python {
    $pythonVersion = & python --version 2>&1
    $version = $pythonVersion -replace 'Python ', ''
    $major, $minor = $version.Split('.')[0..1]
    
    if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 11)) {
        Write-Host "❌ Python 3.11 or higher required. Found: $version" -ForegroundColor Red
        exit 1
    }
    return $version
}

try {
    # Check Python
    Write-Host "[1/5] " -ForegroundColor Blue -NoNewline
    Write-Host "Checking Python version..."
    $PYTHON_VERSION = Check-Python
    Write-Host "✓ Python $PYTHON_VERSION detected" -ForegroundColor Green

    # Create main virtual environment
    Write-Host "[2/5] " -ForegroundColor Blue -NoNewline
    Write-Host "Setting up main project environment..."
    
    Set-Location $SCRIPT_DIR
    
    if (-not (Test-Path ".venv")) {
        & python -m venv .venv
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
    }

    & ".\.venv\Scripts\Activate.ps1"
    
    & python -m pip install --upgrade pip setuptools wheel *>$null
    Write-Host "✓ pip upgraded" -ForegroundColor Green
    
    & pip install -r requirements.txt *>$null
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
    
    # Copy environment file
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Host "✓ Environment file created from .env.example" -ForegroundColor Green
        }
    }

    # Setup MRI Backend
    Write-Host "[3/5] " -ForegroundColor Blue -NoNewline
    Write-Host "Setting up MRI/Neurotract backend..."
    
    Set-Location "$SCRIPT_DIR\MRI\Neurotract"
    
    if (-not (Test-Path ".venv")) {
        & python -m venv .venv
        Write-Host "✓ MRI virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✓ MRI virtual environment already exists" -ForegroundColor Green
    }
    
    & ".\.venv\Scripts\Activate.ps1"
    
    & python -m pip install --upgrade pip setuptools wheel *>$null
    & pip install -r requirements.txt *>$null
    Write-Host "✓ MRI dependencies installed" -ForegroundColor Green

    # Setup MRI Frontend
    Write-Host "[4/5] " -ForegroundColor Blue -NoNewline
    Write-Host "Setting up MRI Frontend (Node.js)..."
    
    Set-Location "$SCRIPT_DIR\MRI\Neurotract\src\frontend"
    
    $nodeInstalled = Get-Command node -ErrorAction SilentlyContinue
    if ($nodeInstalled) {
        $NODE_VERSION = & node --version
        Write-Host "✓ Node.js $NODE_VERSION detected" -ForegroundColor Green
        
        if (-not (Test-Path "node_modules")) {
            & npm install *>$null
            Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
        } else {
            Write-Host "✓ Frontend dependencies already present" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠ Node.js not found. Install Node.js 18+ to use MRI frontend" -ForegroundColor Yellow
        Write-Host "   Download from: https://nodejs.org/" -ForegroundColor Yellow
    }

    # Initialize databases
    Write-Host "[5/5] " -ForegroundColor Blue -NoNewline
    Write-Host "Initializing databases..."
    
    Set-Location $SCRIPT_DIR
    & ".\.venv\Scripts\Activate.ps1"
    
    & python -c "from quadra_diag.db.session import init_db; init_db()" 2>$null | Out-Null
    if ($?) {
        Write-Host "✓ Main database initialized" -ForegroundColor Green
    } else {
        Write-Host "⚠ Main database initialization skipped" -ForegroundColor Yellow
    }

    Write-Host "`n✅ Setup Complete!`n" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Start the platform:  .\startup.ps1" -ForegroundColor Cyan
    Write-Host "  2. Open browser:        http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  3. View MRI analysis:   Click MRI Analysis in navigation`n" -ForegroundColor Cyan

} catch {
    Write-Host "❌ Setup failed: $_" -ForegroundColor Red
    exit 1
}
