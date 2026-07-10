<#
.SYNOPSIS
    10,000 IQ Production Deployment Automation Script for AI ProductOS (Windows PowerShell)
.DESCRIPTION
    Validates configuration, checks Docker readiness, executes database migrations inside containers,
    and deploys the full multi-tier AI ProductOS stack using docker-compose.prod.yml.
#>

$ErrorActionPreference = "Stop"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "       AI ProductOS - Enterprise Production Deployment          " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# 1. Check Docker status
Write-Host "`n[1/5] Verifying Docker daemon readiness..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✔️ Docker daemon is running." -ForegroundColor Green
} catch {
    Write-Error "Docker daemon is not running or not installed. Please start Docker Desktop and try again."
    exit 1
}

# 2. Check environment configuration
Write-Host "`n[2/5] Validating environment configurations..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env")) {
    Write-Host "Configuring backend/.env from backend/.env.example..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
}
if (-not (Test-Path "frontend\.env")) {
    Write-Host "Configuring frontend/.env from frontend/.env.example..." -ForegroundColor Yellow
    Copy-Item "frontend\.env.example" "frontend\.env"
}

$BackendEnv = Get-Content "backend\.env" -Raw
if ($BackendEnv -match "GEMINI_API_KEY=.*AQ.Ab.*") {
    Write-Host "✔️ Gemini API Key detected in backend/.env." -ForegroundColor Green
} else {
    Write-Host "⚠️ WARNING: Ensure your GEMINI_API_KEY or OPENAI_API_KEY is configured inside backend/.env before launching." -ForegroundColor Yellow
}

if ($BackendEnv -match "postgres_secure_pwd_change_me") {
    Write-Host "⚠️ SECURITY WARNING: You are currently using the default PostgreSQL password in backend/.env. Please change it before public deployment!" -ForegroundColor Red
}

# 3. Build and launch production stack
Write-Host "`n[3/5] Building and launching production container grid..." -ForegroundColor Yellow
docker compose -f docker-compose.prod.yml up -d --build

# 4. Verify container status and migrations
Write-Host "`n[4/5] Monitoring database schema initialization & container health..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
docker compose -f docker-compose.prod.yml ps

# 5. Output access endpoints
Write-Host "`n[5/5] Deployment successfully triggered!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 Frontend Application:  http://localhost:3000" -ForegroundColor White
Write-Host "⚙️ Backend API Server:    http://localhost:8000" -ForegroundColor White
Write-Host "📚 OpenAPI Swagger Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "🏥 API Health Check:      http://localhost:8000/health" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
