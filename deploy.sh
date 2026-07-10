#!/usr/bin/env bash
set -e

echo "================================================================"
echo "       AI ProductOS - Enterprise Production Deployment          "
echo "================================================================"

# 1. Check Docker status
echo "[1/5] Verifying Docker daemon readiness..."
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker daemon is not running or not installed. Please start Docker and try again."
    exit 1
fi
echo "✔️ Docker daemon is running."

# 2. Check environment configuration
echo "[2/5] Validating environment configurations..."
if [ ! -f backend/.env ]; then
    echo "Configuring backend/.env from backend/.env.example..."
    cp backend/.env.example backend/.env
fi
if [ ! -f frontend/.env ]; then
    echo "Configuring frontend/.env from frontend/.env.example..."
    cp frontend/.env.example frontend/.env
fi

if grep -q "GEMINI_API_KEY=" backend/.env; then
    echo "✔️ Gemini API Key detected in backend/.env."
else
    echo "⚠️ WARNING: Ensure your GEMINI_API_KEY is configured inside backend/.env before launching."
fi

if grep -q "postgres_secure_pwd_change_me" backend/.env; then
    echo "⚠️ SECURITY WARNING: You are currently using the default PostgreSQL password in backend/.env. Please change it before public deployment!"
fi

# 3. Build and launch production stack
echo "[3/5] Building and launching production container grid..."
docker compose -f docker-compose.prod.yml up -d --build

# 4. Verify container status and migrations
echo "[4/5] Monitoring database schema initialization & container health..."
sleep 10
docker compose -f docker-compose.prod.yml ps

# 5. Output access endpoints
echo "[5/5] Deployment successfully triggered!"
echo "================================================================"
echo "🚀 Frontend Application:  http://localhost:3000"
echo "⚙️ Backend API Server:    http://localhost:8000"
echo "📚 OpenAPI Swagger Docs:  http://localhost:8000/docs"
echo "🏥 API Health Check:      http://localhost:8000/health"
echo "================================================================"
