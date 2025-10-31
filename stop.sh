#!/bin/bash

# Secure E2EE Chat - Stop Script
# This script stops all running services

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🛑 Stopping Secure E2EE Chat Application..."
echo ""

# Stop backend
if lsof -ti:8001 >/dev/null 2>&1; then
    echo "Stopping backend (port 8001)..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Backend stopped"
else
    echo "Backend not running"
fi

# Stop frontend
if lsof -ti:3000 >/dev/null 2>&1; then
    echo "Stopping frontend (port 3000)..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Frontend stopped"
else
    echo "Frontend not running"
fi

# Stop any remaining processes
echo ""
echo "Cleaning up remaining processes..."
pkill -f "uvicorn server:app" 2>/dev/null || true
pkill -f "vite --host" 2>/dev/null || true

echo ""
echo -e "${GREEN}✓ All services stopped${NC}"
