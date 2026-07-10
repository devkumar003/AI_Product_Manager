from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.knowledge.knowledge_base import KnowledgeBase, KnowledgeDocument
from app.ai.rag.rag_engine import (
    InMemoryVectorStore,
    LocalEmbeddingService,
    RAGRetriever,
)
from app.ai.schemas import AgentResponse, AIRequest, AIResponse
from app.ai.services.chat_engine import ChatEngine
from app.ai.services.engine_executor import EngineExecutor
from app.ai.services.export_engine import ExportEngine
from app.ai.services.orchestrator import AIOrchestrator
from app.ai.streaming.streaming_engine import StreamingEngine
from app.ai.workflows.prompt_chaining import WORKFLOW_TEMPLATES
from app.api.v1.deps import (
    get_current_active_user,
    get_db,
    require_workspace_permission,
)
from app.core.permissions import Permission
from app.models.membership import Membership
from app.models.user import User

router = APIRouter()

# ── Singleton service instances ──
orchestrator = AIOrchestrator()
streaming_engine = StreamingEngine()
engine_executor = EngineExecutor(orchestrator.llm_manager, orchestrator.telemetry)
knowledge_base = KnowledgeBase()
_vector_store = InMemoryVectorStore()
_embedding_service = LocalEmbeddingService()
rag_retriever = RAGRetriever(_vector_store, _embedding_service)
chat_engine = ChatEngine(
    orchestrator.llm_manager,
    orchestrator.telemetry,
    knowledge_base=knowledge_base,
    rag_retriever=rag_retriever,
)
export_engine = ExportEngine()

# ── In-memory AI settings store (per-workspace) ──
_ai_settings: dict[str, dict[str, Any]] = {}


# ── Request models ──


class AgentExecutionRequest(BaseModel):
    agent_name: str = Field(..., description="Name of the agent to execute")
    workspace_id: str = Field(..., description="Target workspace ID")
    input_data: dict[str, Any] = Field(
        default_factory=dict, description="Agent-specific input payload"
    )


class EngineRequest(BaseModel):
    engine_name: str = Field(..., description="Name of the engine to run")
    workspace_id: str = Field(default="")
    input_data: dict[str, Any] = Field(default_factory=dict)


class WorkflowRequest(BaseModel):
    workflow_name: str = Field(..., description="Template workflow name")
    workspace_id: str = Field(default="")
    context: dict[str, Any] = Field(default_factory=dict)
    provider: str | None = None
    model: str | None = None


class ChatRequest(BaseModel):
    workspace_id: str = Field(...)
    message: str = Field(...)
    project_id: str | None = None
    provider: str | None = None
    model: str | None = None
    temperature: float = 0.7
    stream: bool = False
    system_prompt_override: str | None = None


class KnowledgeDocRequest(BaseModel):
    collection: str = Field(default="default")
    title: str = Field(...)
    content: str = Field(...)
    category: str = Field(default="general")
    tags: list[str] = Field(default_factory=list)


class ExportRequest(BaseModel):
    data: dict[str, Any] = Field(...)
    format: str = Field(
        default="markdown", description="markdown, json, csv, html, presentation"
    )
    title: str = Field(default="AI ProductOS Export")


class AISettingsUpdate(BaseModel):
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=1.0)
    streaming_enabled: bool = Field(default=True)
    memory_enabled: bool = Field(default=True)
    embeddings_enabled: bool = Field(default=False)
    max_tokens: int = Field(default=4096)
    prompt_template: str = Field(default="")


# ══════════════════════════════════════════════════
# Existing Endpoints (preserved)
# ══════════════════════════════════════════════════


@router.post("/", response_model=AIResponse, status_code=status.HTTP_200_OK)
async def generate_completion(
    req: AIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AIResponse:
    """Unified entry point for AI generation. Routes through agent pipeline if agent_name is set."""
    # Verify workspace membership
    try:
        ws_uuid = UUID(req.workspace_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid workspace ID format"
        ) from e
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == current_user.id,
            Membership.workspace_id == ws_uuid,
            Membership.deleted_at.is_(None),
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for this workspace",
        )

    try:
        req.user_id = str(current_user.id)
        return await orchestrator.execute_request(req)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"AI execution error: {str(e)}"
        ) from e


@router.post("/stream", status_code=status.HTTP_200_OK)
async def generate_stream(
    req: AIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """SSE streaming AI responses."""
    # Verify workspace membership
    try:
        ws_uuid = UUID(req.workspace_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid workspace ID format"
        ) from e
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == current_user.id,
            Membership.workspace_id == ws_uuid,
            Membership.deleted_at.is_(None),
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for this workspace",
        )

    try:
        req.user_id = str(current_user.id)
        token_iterator = orchestrator.execute_stream(req)
        return StreamingResponse(
            streaming_engine.sse_event_generator(token_iterator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"AI streaming error: {str(e)}"
        ) from e


@router.post(
    "/agents/execute", response_model=AgentResponse, status_code=status.HTTP_200_OK
)
async def execute_agent(
    req: AgentExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AgentResponse:
    """Execute a specific agent by name."""
    # Verify workspace membership
    try:
        ws_uuid = UUID(req.workspace_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid workspace ID format"
        ) from e
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == current_user.id,
            Membership.workspace_id == ws_uuid,
            Membership.deleted_at.is_(None),
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for this workspace",
        )

    try:
        return await orchestrator.execute_agent(
            agent_name=req.agent_name,
            workspace_id=req.workspace_id,
            user_id=str(current_user.id),
            input_data=req.input_data,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Agent execution error: {str(e)}"
        ) from e


@router.get("/agents", status_code=status.HTTP_200_OK)
async def list_agents(
    current_user: User = Depends(get_current_active_user),
) -> list[dict[str, Any]]:
    """List all registered agents."""
    return orchestrator.list_agents()


@router.get("/telemetry/{workspace_id}", status_code=status.HTTP_200_OK)
async def get_workspace_telemetry(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> dict:
    """Workspace usage statistics."""
    try:
        return orchestrator.telemetry.get_workspace_summary(str(workspace_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telemetry error: {str(e)}")


# ══════════════════════════════════════════════════
# Task 24: Engine Execution Endpoints
# ══════════════════════════════════════════════════


@router.post("/engines/execute", status_code=status.HTTP_200_OK)
async def execute_engine(
    req: EngineRequest,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Execute a business engine (idea_analysis, prd_generator, etc.)."""
    try:
        result = await engine_executor.execute(
            engine_name=req.engine_name,
            input_data=req.input_data,
            workspace_id=req.workspace_id,
        )
        return {"engine": req.engine_name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine error: {str(e)}")


@router.get("/engines", status_code=status.HTTP_200_OK)
async def list_engines(
    current_user: User = Depends(get_current_active_user),
) -> list[dict[str, str]]:
    """List all available business engines."""
    return engine_executor.list_engines()


# ══════════════════════════════════════════════════
# Workflow Execution Endpoints
# ══════════════════════════════════════════════════


@router.post("/workflows/execute", status_code=status.HTTP_200_OK)
async def execute_workflow(
    req: WorkflowRequest,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Execute a workflow template (idea_validation, prd_generation, etc.)."""
    builder = WORKFLOW_TEMPLATES.get(req.workflow_name)
    if not builder:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{req.workflow_name}' not found. Available: {list(WORKFLOW_TEMPLATES.keys())}",
        )
    try:
        chain = builder(engine_executor)
        result = await chain.execute(
            initial_context=req.context,
            workspace_id=req.workspace_id,
            provider=req.provider,
            model=req.model,
        )
        return {"workflow": req.workflow_name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")


@router.get("/workflows", status_code=status.HTTP_200_OK)
async def list_workflows(
    current_user: User = Depends(get_current_active_user),
) -> list[str]:
    """List available workflow templates."""
    return list(WORKFLOW_TEMPLATES.keys())


# ══════════════════════════════════════════════════
# Chat Endpoints
# ══════════════════════════════════════════════════


@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_active_user),
) -> AIResponse:
    """AI chat with full context awareness."""
    try:
        if req.stream:
            token_iter = chat_engine.chat_stream(
                workspace_id=req.workspace_id,
                user_id=str(current_user.id),
                message=req.message,
                project_id=req.project_id,
                provider=req.provider,
                model=req.model,
                temperature=req.temperature,
            )
            return StreamingResponse(
                streaming_engine.sse_event_generator(token_iter),
                media_type="text/event-stream",
            )
        return await chat_engine.chat(
            workspace_id=req.workspace_id,
            user_id=str(current_user.id),
            message=req.message,
            project_id=req.project_id,
            provider=req.provider,
            model=req.model,
            temperature=req.temperature,
            system_prompt_override=req.system_prompt_override,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ══════════════════════════════════════════════════
# Knowledge Base Endpoints
# ══════════════════════════════════════════════════


@router.post("/knowledge/documents", status_code=status.HTTP_201_CREATED)
async def add_knowledge_document(
    req: KnowledgeDocRequest,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Add a document to the knowledge base."""
    doc = KnowledgeDocument(
        title=req.title, content=req.content, category=req.category, tags=req.tags
    )
    saved = knowledge_base.add_document(req.collection, doc)
    # Also index in RAG
    await rag_retriever.index_document(
        saved.id,
        saved.content,
        metadata={"title": saved.title, "category": saved.category},
    )
    return {"id": saved.id, "collection": req.collection, "title": saved.title}


@router.get("/knowledge/search", status_code=status.HTTP_200_OK)
async def search_knowledge(
    query: str,
    collection: str | None = None,
    category: str | None = None,
    current_user: User = Depends(get_current_active_user),
) -> list[dict[str, Any]]:
    """Search the knowledge base."""
    docs = knowledge_base.search(query, collection_name=collection, category=category)
    return [
        {
            "id": d.id,
            "title": d.title,
            "category": d.category,
            "tags": d.tags,
            "preview": d.content[:200],
        }
        for d in docs
    ]


@router.get("/knowledge/collections", status_code=status.HTTP_200_OK)
async def list_knowledge_collections(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """List knowledge base collections and stats."""
    return knowledge_base.get_stats()


# ══════════════════════════════════════════════════
# Export Endpoints
# ══════════════════════════════════════════════════


@router.post("/export", status_code=status.HTTP_200_OK)
async def export_data(
    req: ExportRequest,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Export AI-generated data to specified format."""
    fmt = req.format.lower()
    if fmt == "markdown":
        content = export_engine.to_markdown(req.data, req.title)
    elif fmt == "json":
        content = export_engine.to_json(req.data)
    elif fmt == "html":
        content = export_engine.to_html(req.data, req.title)
    elif fmt == "csv":
        flat = (
            req.data.get("items", []) if isinstance(req.data.get("items"), list) else []
        )
        content = (
            export_engine.to_csv(flat) if flat else export_engine.to_json(req.data)
        )
    elif fmt == "presentation":
        content = export_engine.to_presentation(req.data, req.title)
    elif fmt == "pdf":
        content = export_engine.to_pdf_ready(req.data, req.title)
    elif fmt == "docx":
        content = export_engine.to_docx_ready(req.data, req.title)
    else:
        content = export_engine.to_json(req.data)

    return {"format": fmt, "title": req.title, "content": content}


# ══════════════════════════════════════════════════
# Task 24: Dashboard Summary
# ══════════════════════════════════════════════════


@router.get("/dashboard/summary", status_code=status.HTTP_200_OK)
async def dashboard_summary(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """AI Dashboard summary with agent count, engine count, knowledge stats."""
    return {
        "agents_registered": len(orchestrator.list_agents()),
        "engines_available": len(engine_executor.list_engines()),
        "workflows_available": len(WORKFLOW_TEMPLATES),
        "knowledge_stats": knowledge_base.get_stats(),
    }


# ══════════════════════════════════════════════════
# Task 26: AI Settings
# ══════════════════════════════════════════════════


@router.get("/settings/{workspace_id}", status_code=status.HTTP_200_OK)
async def get_ai_settings(
    workspace_id: str,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Get AI settings for a workspace."""
    defaults = AISettingsUpdate().model_dump()
    return _ai_settings.get(workspace_id, defaults)


@router.put("/settings/{workspace_id}", status_code=status.HTTP_200_OK)
async def update_ai_settings(
    workspace_id: str,
    settings: AISettingsUpdate,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Update AI settings for a workspace."""
    _ai_settings[workspace_id] = settings.model_dump()
    return _ai_settings[workspace_id]


# ══════════════════════════════════════════════════
# Task: AI Token Usage & FinOps Tracking
# ══════════════════════════════════════════════════


@router.get("/usage/{workspace_id}", status_code=status.HTTP_200_OK)
async def get_ai_token_usage_summary(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Get FinOps token consumption summary and quota status for the workspace."""
    from app.services.ai.ai_usage_service import ai_usage_service

    try:
        ws_uuid = UUID(workspace_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid workspace ID format"
        ) from e

    # Verify workspace membership
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == current_user.id,
            Membership.workspace_id == ws_uuid,
            Membership.deleted_at.is_(None),
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for this workspace",
        )

    return ai_usage_service.get_workspace_usage_summary(db, ws_uuid)
