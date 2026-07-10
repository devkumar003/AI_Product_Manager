from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_current_active_user,
    get_db,
    require_workspace_permission,
)
from app.core.permissions import Permission
from app.models.membership import Membership
from app.models.user import User
from app.repositories.activity import activity_repo
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIGenerateRequest,
    AIGenerateResponse,
)
from app.services.ai.ai_usage_service import ai_usage_service
from app.services.ai.llm_manager import LLMManager
from app.services.ai.memory.conversation import ConversationMemory
from app.services.ai.orchestrator import AIOrchestrator

router = APIRouter()

# Instantiate singletons for the router
llm_manager = LLMManager()
orchestrator = AIOrchestrator(llm_manager=llm_manager)
conversation_memory = ConversationMemory()


@router.get(
    "/{workspace_id}/usage/summary",
    status_code=status.HTTP_200_OK,
)
def get_ai_token_usage_summary(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
):
    """
    Get FinOps token consumption summary and quota status for the workspace.
    """
    summary = ai_usage_service.get_workspace_usage_summary(db, workspace_id)
    return summary


@router.post(
    "/{workspace_id}/generate",
    response_model=AIGenerateResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_product(
    workspace_id: UUID,
    req: AIGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> dict:
    """
    Executes the multi-agent generation flow:
    Product Manager -> PRD Generator -> Technical Architect.
    """
    try:
        results = await orchestrator.run_product_generation_flow(
            raw_idea=req.idea,
            workspace_id=str(workspace_id),
            industry=req.industry,
            model=req.model,
            provider=req.provider,
        )

        # Log to workspace activity timeline
        activity_repo.log(
            db,
            user_id=current_user.id,
            workspace_id=workspace_id,
            action="ai_generation_completed",
            entity_type="workspace",
            entity_id=workspace_id,
            description=f"Generated refined specifications and architecture for: '{results['refined_idea']['refined_title']}'",
        )

        # Record estimated token usage (approx. 450 prompt, 1200 completion tokens)
        ai_usage_service.record_usage(
            db=db,
            workspace_id=workspace_id,
            user_id=current_user.id,
            model=req.model or "gpt-4o",
            prompt_tokens=450,
            completion_tokens=1200,
            provider=req.provider or "openai",
            action_type="product_generation",
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Agent generation pipeline failed: {str(e)}",
        )


@router.post(
    "/{workspace_id}/chat",
    response_model=AIChatResponse,
    status_code=status.HTTP_200_OK,
)
async def chat_with_agent(
    workspace_id: UUID,
    req: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> dict:
    """
    Direct session-based chat with conversational memory context.
    """
    session_id = f"{workspace_id}:{current_user.id}"
    try:
        # 1. Fetch previous conversation memory
        history = await conversation_memory.get_context(session_id)

        # 2. Append new user message
        history.append({"role": "user", "content": req.message})

        # 3. Call LLM Manager
        response_text = await llm_manager.generate(
            messages=history,
            model=req.model,
            provider=req.provider,
        )

        # 4. Save both user message and assistant reply to memory
        await conversation_memory.store(
            session_id,
            [
                {"role": "user", "content": req.message},
                {"role": "assistant", "content": response_text},
            ],
        )

        # Record approximate token usage based on text length
        prompt_len = max(10, len(req.message) // 4)
        comp_len = max(10, len(response_text) // 4)
        ai_usage_service.record_usage(
            db=db,
            workspace_id=workspace_id,
            user_id=current_user.id,
            model=req.model or "gpt-4o",
            prompt_tokens=prompt_len,
            completion_tokens=comp_len,
            provider=req.provider or "openai",
            action_type="chat",
        )

        return {"response": response_text}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent conversational chat pipeline failed: {str(e)}",
        )


@router.post(
    "/{workspace_id}/chat/stream",
    status_code=status.HTTP_200_OK,
)
async def chat_with_agent_stream(
    workspace_id: UUID,
    req: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
):
    """
    Real-time streaming chat endpoint yielding SSE events.
    """
    session_id = f"{workspace_id}:{current_user.id}"
    history = await conversation_memory.get_context(session_id)
    history.append({"role": "user", "content": req.message})

    async def event_generator():
        full_response = ""
        try:
            async for chunk in llm_manager.generate_stream(
                messages=history,
                model=req.model,
                provider=req.provider,
            ):
                full_response += chunk
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
            await conversation_memory.store(
                session_id,
                [
                    {"role": "user", "content": req.message},
                    {"role": "assistant", "content": full_response},
                ],
            )
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post(
    "/{workspace_id}/generate/stream",
    status_code=status.HTTP_200_OK,
)
async def generate_product_spec_stream(
    workspace_id: UUID,
    req: AIGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
):
    """
    Real-time streaming product generation endpoint.
    """
    messages = [
        {
            "role": "system",
            "content": "You are AI ProductOS Senior AI Product Manager and Architect. Generate a detailed specification.",
        },
        {
            "role": "user",
            "content": f"Industry: {req.industry or 'General SaaS'}. Idea: {req.idea}",
        },
    ]

    async def event_generator():
        try:
            async for chunk in llm_manager.generate_stream(
                messages=messages,
                model=req.model,
                provider=req.provider,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
