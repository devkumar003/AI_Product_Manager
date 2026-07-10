class AIException(Exception):
    """Base exception for all AI-related errors."""
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ProviderException(AIException):
    """Raised when an LLM model provider encounters an error."""
    pass


class WorkflowException(AIException):
    """Raised when a workflow engine sequence fails or encounters decision blocks errors."""
    pass


class AgentException(AIException):
    """Raised when an agent validation, schema parsing, or tool mapping error occurs."""
    pass


class ValidationException(AIException):
    """Raised when output formatting or schemas fail to validate against target specs."""
    pass


class RateLimitException(AIException):
    """Raised when request frequency thresholds are breached."""
    pass


class PromptInjectionException(AIException):
    """Raised when prompt input exhibits patterns of prompt injection attacks."""
    pass
