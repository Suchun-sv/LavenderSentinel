# Docker Debugging Guide

## 🚀 Quick Start

### Start Development Environment

```bash
# Start all services (with hot reload)
docker compose up -d

# View logs
docker compose logs -f

# View backend logs only
docker compose logs -f backend

# View frontend logs only
docker compose logs -f frontend
```

### Start with Debug Support

```bash
# Start with development config (debugpy support)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## 🔧 Common Debug Commands

### Check Service Status

```bash
# View all container status
docker compose ps

# View resource usage
docker stats
```

### Enter Containers

```bash
# Enter backend container
docker compose exec backend bash

# Enter frontend container
docker compose exec frontend sh

# Enter database
docker compose exec postgres psql -U postgres -d lavender_sentinel
```

### View Logs

```bash
# Real-time logs for all services
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100

# Filter errors only
docker compose logs -f backend 2>&1 | grep -i error
```

### Restart Services

```bash
# Restart a single service
docker compose restart backend

# Rebuild and restart (after major code changes)
docker compose up -d --build backend

# Full rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 🐛 Python Remote Debugging (debugpy)

### 1. Start Backend with Debug Support

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend
```

### 2. Connect from VS Code / Cursor

1. Open `Run and Debug` panel (Ctrl+Shift+D)
2. Select `Python: Remote Attach (Docker)`
3. Press F5 to start debugging

### 3. Set Breakpoints

Set breakpoints in your code, execution will pause when triggered by requests.

### Manually Trigger Debug (in code)

```python
# Add this where you want to debug
import debugpy
debugpy.breakpoint()
```

## 🔄 Hot Reload

### Backend Hot Reload

Backend uses `uvicorn --reload`, automatically restarts when Python files change.

**Note:** Manual restart required in some cases:
- Modified `pyproject.toml`
- Added new dependencies
- Modified database models (requires migration)

```bash
docker compose restart backend
```

### Frontend Hot Reload

Frontend uses Vite HMR, browser updates automatically when files change.

**If hot reload doesn't work:**

```bash
# Restart frontend
docker compose restart frontend

# Or clear cache
docker compose exec frontend rm -rf .vite
docker compose restart frontend
```

## 🗄️ Database Operations

### Connect to Database

```bash
# Using psql
docker compose exec postgres psql -U postgres -d lavender_sentinel

# Or connect with your favorite database client
# Host: localhost
# Port: 5432
# User: postgres
# Password: postgres
# Database: lavender_sentinel
```

### Common SQL Commands

```sql
-- List all tables
\dt

-- View table structure
\d papers

-- View data
SELECT * FROM papers LIMIT 10;

-- Truncate table
TRUNCATE papers CASCADE;
```

### Reset Database

```bash
# Delete volumes and rebuild
docker compose down -v
docker compose up -d
```

## 📊 Monitor Qdrant Vector Database

Access Qdrant Dashboard: http://localhost:6333/dashboard

## 🧹 Cleanup

```bash
# Stop all services
docker compose down

# Stop and delete volumes
docker compose down -v

# Remove all unused images
docker image prune -a

# Full cleanup (use with caution)
docker system prune -a --volumes
```

## ❓ Troubleshooting

### Q: Backend fails to start with database connection error

```bash
# Wait for database to fully start
docker compose up -d postgres
sleep 5
docker compose up -d backend
```

### Q: Frontend changes not reflected

```bash
# Clear and restart
docker compose exec frontend rm -rf node_modules/.vite
docker compose restart frontend
```

### Q: Want to see full request/response logs

Add middleware or modify log level in `backend/app/main.py`.

### Q: Port already in use

```bash
# Check which process is using the port
lsof -i :8000
lsof -i :5173

# Or modify port mapping in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```
