# 🚀 Deployment Guide - Secure E2EE Chat

## Table of Contents
- [Vercel Deployment](#vercel-deployment)
- [Alternative Deployment Options](#alternative-deployment-options)
- [Environment Variables](#environment-variables)
- [Production Checklist](#production-checklist)
- [Troubleshooting](#troubleshooting)

---

## Vercel Deployment

### Method 1: Deploy via GitHub (Recommended)

#### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Secure E2EE Chat"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

#### Step 2: Import to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect the configuration

#### Step 3: Configure Environment Variables
In Vercel Dashboard → Settings → Environment Variables, add:

**Backend Variables:**
```
SUPABASE_URL=https://jlrwxdudoqxyykfhklck.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres.jlrwxdudoqxyykfhklck:SEllYCUk0XG5lF7u@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
JWT_SECRET_KEY=jpkb3xf0BRoCFELqfn7GJt/htk54i6K25zbP1ijqv7DCrIcktYyaeH3+zvF6OWHB6HZZu6DeVrS94zi0hZCc6w==
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

**Frontend Variables:**
```
REACT_APP_BACKEND_URL=https://your-backend-url.vercel.app
REACT_APP_SUPABASE_URL=https://jlrwxdudoqxyykfhklck.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Step 4: Deploy
1. Click **"Deploy"**
2. Wait for build to complete (~2-5 minutes)
3. Access your application at the provided URL

### ⚠️ Important: WebSocket Limitation on Vercel

**Issue**: Vercel Serverless Functions have limited WebSocket support (10-second timeout).

**Solutions:**

#### Option A: Use Supabase Realtime (Recommended)
Replace WebSocket with Supabase Realtime channels:

1. **Backend**: Remove WebSocket endpoint, use Supabase Realtime API
2. **Frontend**: Use `@supabase/supabase-js` client for real-time subscriptions
3. **Benefit**: Fully serverless, no infrastructure management

#### Option B: Hybrid Deployment
- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Railway/Render for WebSocket support

1. Deploy backend to [Railway](https://railway.app):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

2. Update `REACT_APP_BACKEND_URL` in Vercel to Railway backend URL

---

## Alternative Deployment Options

### Railway (Full-Stack with WebSocket)

1. **Create railway.json**:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "supervisord -c /app/supervisord.conf",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Deploy**:
```bash
railway login
railway init
railway up
```

### Render (Full-Stack with WebSocket)

1. **Create render.yaml**:
```yaml
services:
  - type: web
    name: secure-chat-backend
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
    
  - type: web
    name: secure-chat-frontend
    runtime: node
    buildCommand: cd frontend && yarn install && yarn build
    startCommand: cd frontend && yarn preview --host 0.0.0.0 --port $PORT
```

2. **Deploy**: Connect GitHub repo in Render dashboard

### Docker Deployment

1. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm supervisor

# Install Yarn
RUN npm install -g yarn

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN cd backend && pip install -r requirements.txt
RUN cd frontend && yarn install

# Build frontend
RUN cd frontend && yarn build

# Expose ports
EXPOSE 8001 3000

# Start services
CMD ["supervisord", "-c", "/app/supervisord.conf"]
```

2. **Build and Run**:
```bash
docker build -t secure-chat .
docker run -p 8001:8001 -p 3000:3000 --env-file .env secure-chat
```

---

## Environment Variables

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGc...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | `eyJhbGc...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Random 64-char string |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration (minutes) | `10080` (7 days) |
| `BACKEND_PORT` | Backend server port | `8001` |
| `BACKEND_HOST` | Backend bind address | `0.0.0.0` |

### Frontend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | Backend API URL | `http://localhost:8001` |
| `REACT_APP_SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `REACT_APP_SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGc...` |

---

## Production Checklist

### Security ✅

- [ ] Use HTTPS for all connections
- [ ] Restrict CORS to specific domains (update `server.py`)
- [ ] Rotate JWT secret keys regularly
- [ ] Implement rate limiting on authentication endpoints
- [ ] Enable database connection SSL/TLS
- [ ] Set secure HTTP headers (CSP, HSTS, X-Frame-Options)
- [ ] Implement account lockout after failed login attempts
- [ ] Add request/response logging (without sensitive data)
- [ ] Regular security audits and dependency updates

### Performance 🚀

- [ ] Enable database connection pooling (already configured)
- [ ] Add CDN for frontend static assets
- [ ] Implement Redis for session management (optional)
- [ ] Enable database query optimization and indexing
- [ ] Monitor and optimize WebSocket connections
- [ ] Implement lazy loading for UI components
- [ ] Compress API responses (gzip)
- [ ] Add database read replicas for scaling

### Monitoring 📊

- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Configure uptime monitoring (UptimeRobot, Pingdom)
- [ ] Add application performance monitoring (New Relic, Datadog)
- [ ] Set up log aggregation (Papertrail, Loggly)
- [ ] Create alerting rules for critical errors
- [ ] Monitor database performance metrics
- [ ] Track WebSocket connection metrics

### Database 💾

- [ ] Set up automated backups (Supabase has daily backups)
- [ ] Test backup restoration process
- [ ] Implement database migration strategy
- [ ] Add database performance monitoring
- [ ] Set up replication for high availability
- [ ] Define data retention policies
- [ ] Create database indexes for frequently queried fields

### Scalability 📈

- [ ] Implement horizontal scaling strategy
- [ ] Add load balancer for multiple instances
- [ ] Use message queue for async tasks (optional)
- [ ] Implement caching layer (Redis)
- [ ] Define auto-scaling rules
- [ ] Test under load (load testing with k6, Locust)

### Legal & Compliance 📜

- [ ] Add Terms of Service
- [ ] Add Privacy Policy
- [ ] Implement GDPR compliance (if EU users)
- [ ] Add data export functionality
- [ ] Implement account deletion
- [ ] Add cookie consent banner (if needed)
- [ ] Define data breach notification process

---

## Troubleshooting

### Backend Issues

#### Database Connection Fails
```bash
# Test database connection
python -c "from backend.services.database import engine; print(engine.connect())"

# Check environment variables
cd backend && python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATABASE_URL'))"
```

#### JWT Token Issues
```bash
# Verify JWT secret is set
cd backend && python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(len(os.getenv('JWT_SECRET_KEY', '')))"

# Test token generation
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123","public_key":"test_key"}'
```

#### Port Already in Use
```bash
# Kill process on port 8001
lsof -ti:8001 | xargs kill -9

# Restart backend
cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001
```

### Frontend Issues

#### Build Fails
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules yarn.lock
yarn install
yarn build
```

#### WebSocket Connection Failed
```bash
# Check backend is running
curl http://localhost:8001/health

# Verify WebSocket URL in browser console
# Should be: ws://localhost:8001/ws/{token}
```

#### Environment Variables Not Loading
```bash
# Vite requires REACT_APP_ prefix
# Verify in browser: console.log(import.meta.env.REACT_APP_BACKEND_URL)

# Restart dev server after .env changes
yarn dev
```

### Database Issues

#### Tables Not Created
```bash
# Run Python script to create tables
cd backend
python -c "from models.user import Base as UserBase; from models.message import Base as MessageBase; from services.database import engine; UserBase.metadata.create_all(bind=engine); MessageBase.metadata.create_all(bind=engine); print('Tables created')"
```

#### Migration Needed
```bash
# Install Alembic for migrations
pip install alembic

# Initialize Alembic
cd backend
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Common Errors

#### "Private key not found"
- User registered on different device/browser
- IndexedDB was cleared
- Solution: Re-register with same username (will fail) or use different username

#### "CORS error"
- Backend CORS not configured for frontend domain
- Solution: Update `allow_origins` in `backend/server.py`

#### "WebSocket disconnected"
- Backend crashed or restarted
- Network connectivity issue
- Solution: Frontend auto-reconnects after 3 seconds

---

## Performance Benchmarks

### Expected Performance

- **Registration**: ~500ms (includes key generation)
- **Login**: ~200ms
- **Message Encryption**: ~10ms (RSA-OAEP 2048-bit)
- **Message Decryption**: ~15ms
- **WebSocket Latency**: <50ms (local), <200ms (global)
- **API Response Time**: <100ms (90th percentile)

### Load Testing

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io

# Create load test script (test.js)
cat > test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  let res = http.get('http://localhost:8001/health');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}
EOF

# Run load test
k6 run test.js
```

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review backend logs: `tail -f /var/log/supervisor/backend.err.log`
3. Review frontend logs in browser console (F12)
4. Check Supabase dashboard for database issues

---

**Production Deployment Recommendation:**
- **Frontend**: Vercel (fast, free, CDN included)
- **Backend**: Railway or Render (WebSocket support)
- **Database**: Supabase (managed Postgres, free tier generous)

This setup provides the best balance of performance, cost, and ease of management.
