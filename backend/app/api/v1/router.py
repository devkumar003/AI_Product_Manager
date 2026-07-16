from fastapi import APIRouter

from app.ai.router import router as ai_router
from app.api.v1.endpoints import (
    activities,
    auth,
    development,
    documents,
    executive,
    health,
    integration,
    invitations,
    notifications,
    organizations,
    orchestrator,
    planning,
    projects,
    search,
    users,
    websockets,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(
    invitations.router, prefix="/invitations", tags=["invitations"]
)
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(
    orchestrator.router, prefix="/orchestrator", tags=["orchestrator"]
)
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(planning.router, prefix="/planning", tags=["planning"])
api_router.include_router(
    integration.router, prefix="/integration", tags=["integration"]
)
api_router.include_router(
    development.router, prefix="/development", tags=["development"]
)
api_router.include_router(executive.router, prefix="/executive", tags=["executive"])
api_router.include_router(websockets.router, tags=["websockets"])
