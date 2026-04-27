#!/bin/bash

# QuadraDiag + NeuroTract Unified Startup Script (Linux/macOS)
# Starts all services required for the integrated platform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🏥 QuadraDiag + NeuroTract Integrated Platform  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Function to clean up on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}⚠ Shutting down services...${NC}"
    jobs -p | xargs -r kill 2>/dev/null || true
    echo -e "${BLUE}Services stopped${NC}"
}

trap cleanup EXIT INT TERM

# Check if setup is complete
if [ ! -d ".venv" ] || [ ! -d "MRI/Neurotract/.venv" ]; then
    echo -e "${YELLOW}⚠ Setup not complete. Running setup first...${NC}"
    chmod +x "$SCRIPT_DIR/setup.sh"
    "$SCRIPT_DIR/setup.sh"
fi

# Start Main QuadraDiag Backend
echo -e "${BLUE}[1/4]${NC} Starting QuadraDiag Backend (Port 8000)..."
cd "$SCRIPT_DIR"
source .venv/bin/activate

python app.py &
MAIN_PID=$!
echo -e "${GREEN}✓${NC} PID: $MAIN_PID"
sleep 2

# Start MRI Backend
echo -e "${BLUE}[2/4]${NC} Starting NeuroTract Backend (Port 8001)..."
cd "$SCRIPT_DIR/MRI/Neurotract"
source .venv/bin/activate

python -m uvicorn src.backend.api.server:app --host 127.0.0.1 --port 8001 --reload &
MRI_BACKEND_PID=$!
echo -e "${GREEN}✓${NC} PID: $MRI_BACKEND_PID"
sleep 2

# Start MRI Frontend
echo -e "${BLUE}[3/4]${NC} Starting NeuroTract Frontend (Port 3000)..."
if command -v node &> /dev/null; then
    cd "$SCRIPT_DIR/MRI/Neurotract/src/frontend"
    npm run dev &
    MRI_FRONTEND_PID=$!
    echo -e "${GREEN}✓${NC} PID: $MRI_FRONTEND_PID"
    sleep 3
else
    echo -e "${YELLOW}⚠ Node.js not found. Skipping MRI Frontend${NC}"
    echo "   Install Node.js 18+ from: https://nodejs.org/"
fi

echo ""
echo -e "${BLUE}[4/4]${NC} Service Status:"
echo ""
echo -e "  ${GREEN}✓ Main Platform${NC}     → ${CYAN}http://localhost:8000${NC}"
echo -e "     Dashboard          → ${CYAN}http://localhost:8000/dashboard${NC}"
echo -e "     API Documentation  → ${CYAN}http://localhost:8000/docs${NC}"
echo ""
echo -e "  ${GREEN}✓ NeuroTract Backend${NC}  → ${CYAN}http://localhost:8001${NC}"
echo -e "     API Documentation  → ${CYAN}http://localhost:8001/docs${NC}"
echo ""
if command -v node &> /dev/null; then
    echo -e "  ${GREEN}✓ NeuroTract Frontend${NC} → ${CYAN}http://localhost:3000${NC}"
    echo ""
fi

echo -e "${BLUE}Features Available:${NC}"
echo -e "  • Diabetes Risk Assessment"
echo -e "  • Heart Disease Risk Assessment"
echo -e "  • Liver Disease Risk Assessment"
echo -e "  • Parkinson's Risk Assessment"
echo -e "  • ${YELLOW}NEW:${NC} Brain MRI Analysis (NeuroTract)"
echo ""
echo -e "${YELLOW}To exit, press Ctrl+C${NC}"
echo ""

# Keep script running
wait
