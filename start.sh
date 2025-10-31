#!/bin/bash

# Secure E2EE Chat - Startup Script
# This script starts both backend and frontend services

set -e

echo "🚀 Starting Secure E2EE Chat Application..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} Port $1 is already in use"
        echo "  Killing process on port $1..."
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f -o /dev/null $url; then
            echo -e "${GREEN}✓${NC} $name is running"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}✗${NC} $name failed to start"
    return 1
}

# Check and kill processes on ports
echo "📡 Checking ports..."
check_port 8001
check_port 3000
echo ""

# Check environment files
echo "🔧 Checking environment files..."
if [ ! -f "/app/backend/.env" ]; then
    echo -e "${RED}✗${NC} Backend .env file not found"
    exit 1
else
    echo -e "${GREEN}✓${NC} Backend .env found"
fi

if [ ! -f "/app/frontend/.env" ]; then
    echo -e "${RED}✗${NC} Frontend .env file not found"
    exit 1
else
    echo -e "${GREEN}✓${NC} Frontend .env found"
fi
echo ""

# Start backend
echo "🐍 Starting Backend (FastAPI)..."
cd /app/backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 > /var/log/supervisor/backend.out.log 2>&1 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "  Waiting for backend to start..."
if check_service "http://localhost:8001/health" "Backend"; then
    echo ""
else
    echo -e "${RED}Backend failed to start. Check logs: tail -f /var/log/supervisor/backend.err.log${NC}"
    exit 1
fi

# Start frontend
echo "⚛️  Starting Frontend (React)..."
cd /app/frontend
yarn dev --host 0.0.0.0 --port 3000 > /var/log/supervisor/frontend.out.log 2>&1 &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo "  Waiting for frontend to start..."
sleep 5
if check_service "http://localhost:3000" "Frontend"; then
    echo ""
else
    echo -e "${YELLOW}Frontend may still be starting. Check logs: tail -f /var/log/supervisor/frontend.out.log${NC}"
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Secure E2EE Chat Application Started Successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Service URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8001"
echo "   API Docs:  http://localhost:8001/docs"
echo ""
echo "📊 Process IDs:"
echo "   Backend:   $BACKEND_PID"
echo "   Frontend:  $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:   tail -f /var/log/supervisor/backend.out.log"
echo "   Frontend:  tail -f /var/log/supervisor/frontend.out.log"
echo "   Errors:    tail -f /var/log/supervisor/*.err.log"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or: pkill -f 'uvicorn|vite'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
