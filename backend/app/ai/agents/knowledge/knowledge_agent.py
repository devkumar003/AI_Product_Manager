from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class KnowledgeAgentInput(BaseModel):
    document_content: str = Field(..., description="Raw text document to load/index")
    query: str = Field(default="", description="Search query if retrieving context")


class KnowledgeAgent(BaseAgent[KnowledgeAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "knowledge"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Architecture stubs for indexing external docs, loading knowledge files, "
            "and retrieving semantic vector contents (future RAG integration)."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Knowledge Agent. Formulate knowledge embeddings structures, document catalogs, and vector mappings.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- load_status: string\n"
            "- document_metadata: dict of (source, char_count, tags)\n"
            "- index_mappings: list of dicts (chunk_id, keywords)\n"
            "- retrieval_suggestions: list of strings"
        )
