"""
Task 20 — AI Chat Engine

Full-featured chat engine with:
- Streaming via LLM Manager
- Conversation history management
- Context awareness (workspace, project, memory, knowledge)
- Multi-turn conversations
- Markdown/code block support (handled by frontend rendering)
"""

import logging
import time
from collections.abc import AsyncIterator

from app.ai.core.llm_manager import LLMManager
from app.ai.knowledge.knowledge_base import KnowledgeBase
from app.ai.memory.enhanced_memory import LongTermMemory, MemoryRetriever, ProjectMemory
from app.ai.memory.memory_manager import (
    ConversationMemory,
    OrganizationMemory,
    WorkspaceMemory,
)
from app.ai.rag.rag_engine import RAGRetriever
from app.ai.schemas import AIResponse, StreamingToken
from app.ai.telemetry.metrics import TelemetryRegistry
from app.ai.utils.security import AISecurityManager

logger = logging.getLogger("app.ai.chat_engine")


class ChatEngine:
    """
    Enterprise chat engine supporting multi-turn conversations
    with full context awareness across workspace, project, memory, and knowledge layers.
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        telemetry: TelemetryRegistry,
        knowledge_base: KnowledgeBase | None = None,
        rag_retriever: RAGRetriever | None = None,
    ) -> None:
        self.llm = llm_manager
        self.telemetry = telemetry
        self.knowledge_base = knowledge_base
        self.rag_retriever = rag_retriever

        # Memory layers
        self.conversation_memory = ConversationMemory(limit=20)
        self.workspace_memory = WorkspaceMemory()
        self.organization_memory = OrganizationMemory()
        self.project_memory = ProjectMemory()
        self.long_term_memory = LongTermMemory()

        self.memory_retriever = MemoryRetriever(
            conversation=self.conversation_memory,
            workspace=self.workspace_memory,
            organization=self.organization_memory,
            project=self.project_memory,
            long_term=self.long_term_memory,
        )

    async def chat(
        self,
        workspace_id: str,
        user_id: str,
        message: str,
        project_id: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        system_prompt_override: str | None = None,
    ) -> AIResponse:
        """Synchronous chat completion with full context loading."""
        start_time = time.time()

        # Security
        AISecurityManager.verify_prompt_injection(message)
        sanitized = AISecurityManager.sanitize_input(message)

        # Build context-enriched messages
        messages = await self._build_messages(
            workspace_id, user_id, project_id, sanitized, system_prompt_override
        )

        # Execute
        response = await self.llm.generate(
            messages=messages,
            provider=provider,
            model=model,
            temperature=temperature,
        )

        masked = AISecurityManager.mask_secrets(response.content)
        response.content = masked

        # Save to memory
        session_id = self._session_key(workspace_id, user_id)
        await self.conversation_memory.store(
            session_id,
            [
                {"role": "user", "content": sanitized},
                {"role": "assistant", "content": masked},
            ],
        )

        # Telemetry
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_request(
            workspace_id=workspace_id,
            provider=response.provider,
            model=response.model,
            tokens=response.usage.total_tokens,
            cost=response.usage.estimated_cost_usd,
            latency_ms=latency,
            success=True,
        )

        return response

    async def chat_stream(
        self,
        workspace_id: str,
        user_id: str,
        message: str,
        project_id: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[StreamingToken]:
        """Streaming chat with full context awareness."""
        AISecurityManager.verify_prompt_injection(message)
        sanitized = AISecurityManager.sanitize_input(message)

        messages = await self._build_messages(
            workspace_id, user_id, project_id, sanitized
        )

        async for token in self.llm.stream(
            messages=messages,
            provider=provider,
            model=model,
            temperature=temperature,
        ):
            yield token

    async def _build_messages(
        self,
        workspace_id: str,
        user_id: str,
        project_id: str | None,
        user_message: str,
        system_override: str | None = None,
    ) -> list[dict[str, str]]:
        """Assemble messages with all context layers."""
        system_prompt = system_override or (
            "You are AI ProductOS Assistant — an enterprise AI product management platform.\n"
            "Help users plan products, analyze ideas, review architectures, and manage sprints.\n"
            "Support markdown formatting, code blocks, tables, and structured JSON when appropriate.\n"
            "Be thorough, professional, and actionable."
        )

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

        # Memory context
        session_id = self._session_key(workspace_id, user_id)
        memory_key = project_id or session_id

        all_ctx = await self.memory_retriever.retrieve_all(memory_key)
        messages.extend(all_ctx)

        # RAG context if available
        if self.rag_retriever:
            try:
                chunks = await self.rag_retriever.retrieve(user_message, top_k=3)
                if chunks:
                    rag_text = "\n\n".join(f"[Knowledge] {c.content}" for c in chunks)
                    messages.append({"role": "system", "content": rag_text})
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")

        # Knowledge base context if available
        if self.knowledge_base:
            try:
                docs = self.knowledge_base.search(user_message, limit=3)
                if docs:
                    kb_text = "\n".join(
                        f"[KB:{d.category}] {d.content[:300]}" for d in docs
                    )
                    messages.append({"role": "system", "content": kb_text})
            except Exception as e:
                logger.warning(f"Knowledge base search failed: {e}")

        # Conversation history
        history = await self.conversation_memory.get_context(session_id)
        messages.extend(history)

        # User message
        messages.append({"role": "user", "content": user_message})

        return messages

    @staticmethod
    def _session_key(workspace_id: str, user_id: str) -> str:
        return f"{workspace_id}:{user_id}"
