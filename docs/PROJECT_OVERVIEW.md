# AI ProductOS: Project Overview

AI ProductOS is a comprehensive, multi-agent AI Product Management suite. It acts as an autonomous requirements engineer, technical architect, sprint planner, financial modeler, and developer sandbox, consolidating standard product management operations with advanced LLM agent coordination.

---

## 🏗️ System Architecture

The application is structured as a decoupled monorepo containing a FastAPI Python backend and a Next.js React frontend.

```
AI_Product_Manager/
├── backend/                # Python FastAPI Backend
│   ├── app/
│   │   ├── ai/             # Agent Prompting & Telemetry
│   │   ├── api/            # Route Endpoints (/v1)
│   │   ├── core/           # Security, Config & Redis
│   │   ├── database/       # SQLAlchemy Base & Session
│   │   ├── models/         # SQLAlchemy DB Tables
│   │   ├── repositories/   # DB Operations (CRUD)
│   │   ├── schemas/        # Pydantic Schemas
│   │   └── services/       # Core Business Logic & Engines
│   └── alembic/            # Database Migrations
└── frontend/               # Next.js React Frontend
    ├── src/
    │   ├── app/            # App Router Pages
    │   ├── components/     # UI Components (Shell, Cards, Inputs)
    │   ├── context/        # AuthContext State Provider
    │   └── lib/            # Axios API Configuration
```

### 1. Frontend Subsystem
*   **Core**: Next.js 16 (App Router), React 19, TypeScript.
*   **Styling**: Vanilla CSS, TailwindCSS, Framer Motion (for animations).
*   **Data Fetching**: Axios, React Query.
*   **UI Kit**: Lucide React icons, shadcn-inspired modular dashboard widgets.

### 2. Backend Subsystem
*   **Web Framework**: FastAPI (ASGI server run via Uvicorn).
*   **Database ORM**: SQLAlchemy (supporting PostgreSQL/SQLite).
*   **Migration Tool**: Alembic.
*   **Task Queue & Cache**: Redis (for caching, rate-limiting, and blacklists).
*   **AI Service**: ChatEngine & Workflow executors supporting OpenAI, Gemini, Anthropic, Groq, and DeepSeek.

### 3. Database & Storage
*   **Relational DB**: SQLite (local dev/test) or PostgreSQL (production).
*   **Data Models**:
    *   `users`: Handles credentials, preferences, verified flags, last login.
    *   `organizations` & `workspaces`: Multitenant scoping structures.
    *   `memberships` & `invitations`: Workspace-level role control.
    *   `projects`: Main containers for goals, stories, and code codebases.
    *   `chat_messages`: Memory history for conversational sessions.
    *   `audit_logs`: Records of agent calls, user actions, and modifications.
*   **File Storage**: Local directory storage (e.g. `uploads/` folder with read/write safety) or scalable cloud buckets.

### 4. Authentication & Security
*   **Session Token**: JWT (JSON Web Tokens) with asymmetric signing secrets.
*   **Flow**: User supplies credentials to `/auth/login`, receives access and refresh tokens, which are stored in `localStorage` and sent via `Authorization: Bearer <token>` headers.
*   **Security Middlewares**: CORS controls, rate-limiting, request size limits, and security headers.

---

## 🌟 Core Features

1.  **Autonomous Swarm Engineering**: Orchestrates 5 agents (Market Research, Product Discovery, Business Analyst, UX Design, and Executive Review) sequentially to craft full PRD documents.
2.  **Dedicated Intelligence Suite**: Integrates PESTLE market research, SWOT analysis, competitor landscape mapping, risk logs, and financial cost estimations.
3.  **Sprint Planner & Scheduler**: Tracks tasks, backlogs, and automates work schedules using LLM scheduling agents.
4.  **DevOps & Code Sandbox**: Generates code frameworks, tests, and deploys scripts to multiple target platforms (AWS, GCP, Render).
5.  **FinOps & Observability**: Logs token metrics, latency, and operational expense counts in real-time.
