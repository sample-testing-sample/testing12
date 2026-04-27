# QuadraDiag + NeuroTract Unified Startup Script (Windows PowerShell)
# Starts all services required for the integrated platform

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🏥 QuadraDiag + NeuroTract Integrated Platform  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# Function to handle cleanup
$processes = @()

function Cleanup {
    Write-Host "`n⚠ Shutting down services..." -ForegroundColor Yellow
    
    foreach ($proc in $processes) {
        if ($proc) {
            try {
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            } catch {}
        }
    }
    
    Write-Host "Services stopped" -ForegroundColor Blue
}

$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Cleanup }

# Check if setup is complete
if (-not (Test-Path ".venv")) {
    Write-Host "⚠ Setup not complete. Running setup first..." -ForegroundColor Yellow
    & "$SCRIPT_DIR\setup.ps1"
}

# Windows function to start process and track it
function Start-ServiceProcess {
    param(
        [string]$Label,
        [int]$Index,
        [string]$WorkingDirectory,
        [string]$Command,
        [int]$Port,
        [int]$WaitSeconds = 2
    )
    
    Write-Host "[$Index/4] " -ForegroundColor Blue -NoNewline
    Write-Host "Starting $Label (Port $Port)..."
    
    Push-Location $WorkingDirectory
    
    $scriptBlock = {
        param($cmd)
        Invoke-Expression $cmd
    }
    
    $proc = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoExit -Command &{$Command}" `
        -PassThru `
        -WorkingDirectory $WorkingDirectory
    
    $global:processes += $proc
    Write-Host "✓ PID: " -ForegroundColor Green -NoNewline
    Write-Host "$($proc.Id)"
    
    Pop-Location
    Start-Sleep -Seconds $WaitSeconds
}

try {
    # Start Main Backend
    Start-ServiceProcess `
        -Label "QuadraDiag Backend" `
        -Index 1 `
        -WorkingDirectory $SCRIPT_DIR `
        -Command ".\.venv\Scripts\Activate.ps1; python app.py" `
        -Port 8000

    # Start MRI Backend
    Start-ServiceProcess `
        -Label "NeuroTract Backend" `
        -Index 2 `
        -WorkingDirectory "$SCRIPT_DIR\MRI\Neurotract" `
        -Command ".\.venv\Scripts\Activate.ps1; python -m uvicorn src.backend.api.server:app --host 127.0.0.1 --port 8001 --reload" `
        -Port 8001

    # Start MRI Frontend
    $nodeInstalled = Get-Command node -ErrorAction SilentlyContinue
    if ($nodeInstalled) {
        Start-ServiceProcess `
            -Label "NeuroTract Frontend" `
            -Index 3 `
            -WorkingDirectory "$SCRIPT_DIR\MRI\Neurotract\src\frontend" `
            -Command "npm run dev" `
            -Port 3000 `
            -WaitSeconds 3
    } else {
        Write-Host "[3/4] " -ForegroundColor Blue -NoNewline
        Write-Host "Starting NeuroTract Frontend (Port 3000)..." -NoNewline
        Write-Host " ⚠ Node.js not found" -ForegroundColor Yellow
        Write-Host "   Install Node.js 18+ from: https://nodejs.org/"
    }

    Write-Host "`n[4/4] " -ForegroundColor Blue -NoNewline
    Write-Host "Service Status:`n"

    Write-Host "  ✓ Main Platform" -ForegroundColor Green -NoNewline
    Write-Host "     → " -NoNewline
    Write-Host "http://localhost:8000" -ForegroundColor Cyan
    Write-Host "     Dashboard          → " -NoNewline
    Write-Host "http://localhost:8000/dashboard" -ForegroundColor Cyan
    Write-Host "     API Documentation  → " -NoNewline
    Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "  ✓ NeuroTract Backend" -ForegroundColor Green -NoNewline
    Write-Host "  → " -NoNewline
    Write-Host "http://localhost:8001" -ForegroundColor Cyan
    Write-Host "     API Documentation  → " -NoNewline
    Write-Host "http://localhost:8001/docs" -ForegroundColor Cyan
    
    if ($nodeInstalled) {
        Write-Host ""
        Write-Host "  ✓ NeuroTract Frontend" -ForegroundColor Green -NoNewline
        Write-Host " → " -NoNewline
        Write-Host "http://localhost:3000" -ForegroundColor Cyan
    }

    Write-Host "`nFeatures Available:" -ForegroundColor Blue
    Write-Host "  • Diabetes Risk Assessment"
    Write-Host "  • Heart Disease Risk Assessment"
    Write-Host "  • Liver Disease Risk Assessment"
    Write-Host "  • Parkinson's Risk Assessment"
    Write-Host "  • " -NoNewline
    Write-Host "NEW: " -ForegroundColor Yellow -NoNewline
    Write-Host "Brain MRI Analysis (NeuroTract)"

    Write-Host "`n" -NoNewline
    Write-Host "To exit, close this window or press Ctrl+C" -ForegroundColor Yellow
    Write-Host "`n"

    # Keep running
    do {
        Start-Sleep -Seconds 1
    } while ($true)

} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Cleanup
    exit 1
}
