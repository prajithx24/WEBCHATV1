#!/bin/bash

# Secure E2EE Chat - Status Check Script

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "📊 Secure E2EE Chat - Service Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check backend
echo "🐍 Backend (FastAPI):"
if curl -s -f -o /dev/null http://localhost:8001/health; then
    echo -e "   Status: ${GREEN}✓ Running${NC}"
    echo "   URL: http://localhost:8001"
    echo "   API Docs: http://localhost:8001/docs"
    BACKEND_PID=$(lsof -ti:8001)
    echo "   PID: $BACKEND_PID"
else
    echo -e "   Status: ${RED}✗ Not Running${NC}"
fi
echo ""

# Check frontend
echo "⚛️  Frontend (React):"
if curl -s -f -o /dev/null http://localhost:3000; then
    echo -e "   Status: ${GREEN}✓ Running${NC}"
    echo "   URL: http://localhost:3000"
    FRONTEND_PID=$(lsof -ti:3000)
    echo "   PID: $FRONTEND_PID"
else
    echo -e "   Status: ${RED}✗ Not Running${NC}"
fi
echo ""

# Check database connectivity
echo "💾 Database (PostgreSQL):"
cd /app/backend
if python -c "from services.database import engine; engine.connect(); print('Connected')" 2>/dev/null | grep -q "Connected"; then
    echo -e "   Status: ${GREEN}✓ Connected${NC}"
else
    echo -e "   Status: ${RED}✗ Connection Failed${NC}"
fi
echo ""

# Recent logs
echo "📝 Recent Logs (last 5 lines):"
echo ""
echo "Backend:"
tail -n 5 /var/log/supervisor/backend.out.log 2>/dev/null || echo "  No logs found"
echo ""
echo "Frontend:"
tail -n 5 /var/log/supervisor/frontend.out.log 2>/dev/null || echo "  No logs found"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
