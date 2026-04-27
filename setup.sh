#!/bin/bash

# QuadraDiag + NeuroTract Unified Setup Script (Linux/macOS)
# This script sets up both projects with their dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🏥 QuadraDiag + NeuroTract Setup"
echo "=================================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}[1/5]${NC} Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [[ $MAJOR -lt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -lt 11 ]]; then
    echo "❌ Python 3.11 or higher required. Found: $PYTHON_VERSION"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"

# Create main virtual environment
echo -e "${BLUE}[2/5]${NC} Setting up main project environment..."
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

source .venv/bin/activate

pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "✓ pip upgraded"

pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Copy environment file if needed
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Environment file created from .env.example"
    fi
fi

# Setup MRI/Neurotract
echo -e "${BLUE}[3/5]${NC} Setting up MRI/Neurotract backend..."
cd "$SCRIPT_DIR/MRI/Neurotract"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ MRI virtual environment created"
else
    echo "✓ MRI virtual environment already exists"
fi

source .venv/bin/activate

pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ MRI dependencies installed"

# Setup MRI Frontend
echo -e "${BLUE}[4/5]${NC} Setting up MRI Frontend (Node.js)..."
cd "$SCRIPT_DIR/MRI/Neurotract/src/frontend"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js $NODE_VERSION detected"
    
    if [ ! -d "node_modules" ]; then
        npm install > /dev/null 2>&1
        echo "✓ Frontend dependencies installed"
    else
        echo "✓ Frontend dependencies already present"
    fi
else
    echo -e "${YELLOW}⚠${NC} Node.js not found. Install Node.js 18+ to use MRI frontend"
    echo "   Download from: https://nodejs.org/"
fi

# Initialize databases
echo -e "${BLUE}[5/5]${NC} Initializing databases..."
cd "$SCRIPT_DIR"
source .venv/bin/activate

python3 -c "from quadra_diag.db.session import init_db; init_db()" 2>/dev/null && echo "✓ Main database initialized" || echo "⚠ Main database initialization skipped"

echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the platform:  ${BLUE}./startup.sh${NC}"
echo "  2. Open browser:        ${BLUE}http://localhost:8000${NC}"
echo "  3. View MRI analysis:   Click ${BLUE}MRI Analysis${NC} in navigation"
echo ""
