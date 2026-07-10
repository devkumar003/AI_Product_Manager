# AI ProductOS - Enterprise AI-Powered Product Management Platform

AI ProductOS is a production-ready, enterprise-grade SaaS platform designed for modern product management, featuring real-time collaborative workspace tools, structured document management, and modular architecture prepared for advanced AI integrations.

## 🏗️ Architecture Overview

The system is structured as a monorepo containing a high-performance backend, an optimized web frontend, and shared schemas/validators:

```
AI-ProductOS/
├── backend/            # FastAPI Backend
│   ├── app/
│   │   ├── api/        # Routers & API Endpoints (v1)
│   │   ├── core/       # Configurations, Security, Logging
│   │   ├── database/   # SQLAlchemy Models, Session, Migrations
│   │   ├── middleware/ # Global exception & validation middlewares
│   │   ├── models/     # DB Entities
│   │   ├── schemas/    # Pydantic Schemas
│   │   ├── services/   # Business Logic
│   │   ├── repositories/# Database Access Layer (SOLID Repository Pattern)
│   │   ├── utils/      # Standard utility functions
│   │   └── main.py     # Application entrypoint
│   └── tests/          # Pytest Suite
├── frontend/           # Next.js Frontend (App Router, Tailwind, TypeScript, shadcn/ui)
│   ├── app/            # App routes & shells
│   ├── components/     # Reusable UI components
│   ├── hooks/          # React hooks
│   ├── lib/            # Utilities (Axios config, API clients)
│   ├── services/       # Front-end service modules
│   └── types/          # TypeScript definitions
├── shared/             # Shared TS types, constants, and validators
├── docker/             # Docker configuration files
├── docs/               # System and API Documentation
└── scripts/            # Build and utility scripts
```

## 🛠️ Tech Stack

### Backend
* **FastAPI** (Python 3.12) - High performance async API framework.
* **SQLAlchemy 2.0** - Type-safe ORM for relational queries.
* **Alembic** - Database migrations.
* **Pydantic v2** - Data validation and settings management.
* **PostgreSQL & Redis** - Relational storage & caching/session store.
* **Uvicorn** - ASGI server.

### Frontend
* **Next.js 15 (App Router)** - React framework.
* **TypeScript** - Strict type safety.
* **TailwindCSS** - Style compilation.
* **shadcn/ui** - Highly polished accessible UI primitives.
* **Axios** - Typed request orchestration with interceptors.
* **Zod** - Form validation.

### DevOps & QA
* **Docker & Docker Compose** - Container orchestrator.
* **GitHub Actions** - CI/CD pipeline automation.
* **Prettier, ESLint, Ruff, Black** - Quality tooling.

---

## 🚀 Getting Started

### Prerequisites
* Docker & Docker Compose
* Node.js v18+ & npm
* Python 3.12+

### Running with Docker (Recommended for Development)
1. Clone this repository.
2. Initialize environment configs:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```
3. Run the orchestration stack:
   ```bash
   docker compose up --build
   ```
4. Access applications:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - Swagger Documentation: `http://localhost:8000/docs`

### Enterprise Production Deployment (`docker-compose.prod.yml`)
For cloud production environments (AWS, Google Cloud Run, DigitalOcean, or self-hosted servers), run our single-click automated deployment script:
* **Windows (PowerShell)**:
  ```powershell
  .\deploy.ps1
  ```
* **Linux / macOS**:
  ```bash
  chmod +x deploy.sh && ./deploy.sh
  ```
Or manually launch the production orchestration grid with automated database schema initialization (`docker-entrypoint.sh`):
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Running Locally for Development

#### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔒 Security & Quality Standards
* **Secrets Management**: No secrets committed to git. Validator checks env parameters on boot.
* **Exception Handlers**: Global middleware converts errors to standardized format.
* **Strict Type Safety**: TypeScript on frontend, Pydantic on backend.
