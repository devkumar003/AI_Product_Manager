import logging
import re

from app.ai.exceptions import PromptInjectionException

logger = logging.getLogger("app.ai.security")


class AISecurityManager:
    """
    Manages security boundary verification: prompt injection checks, sanitization,
    secret masks, and content verification.
    """

    # Common prompt injection sequences to catch
    INJECTION_PATTERNS = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"system\s+(?:reset|override)",
        r"you\s+are\s+now\s+an\s+admin",
        r"disregard\s+prior\s+rules",
        r"new\s+role:\s*",
        r"bypass\s+restrictions",
        r"do\s+anything\s+now",
        r"dan\s+mode",
        r"jailbreak",
        r"assistant\s+instruction\s+override",
        r"unauthorized\s+injection",
        r"malicious\s+exploit",
        r"ignore\s+above\s+and\s+do",
        r"read\s+all\s+system\s+prompts",
        r"output\s+the\s+system\s+prompt\s+above",
    ]

    # Patterns to detect api keys/secrets in text
    SECRET_PATTERNS = [
        r"(?:sk-[a-zA-Z0-9]{32,48})",  # OpenAI
        r"(?:AIzaSy[a-zA-Z0-9\-_]{33})",  # Google Gemini
        r"(?:Bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*)",  # Standard JWT/bearer tokens
    ]

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """Wipes potentially unsafe HTML/script blocks and cleans double escapes."""
        cleaned = re.sub(
            r"<script.*?>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE
        )
        # Strips out HTML elements generally to ensure raw text
        cleaned = re.sub(r"<[^>]*>", "", cleaned)
        return cleaned.strip()

    @classmethod
    def verify_prompt_injection(cls, text: str) -> None:
        """Scan input for common prompt injection patterns. Raises PromptInjectionException if matched."""
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Prompt injection pattern matched on: {pattern}")
                raise PromptInjectionException(
                    message="Malicious input pattern detected. Request rejected by safety systems.",
                    details={"matched_pattern": pattern},
                )

    @classmethod
    def mask_secrets(cls, text: str) -> str:
        """Detect and mask private API credentials or tokens present in model responses or system prompts."""
        masked = text
        for pattern in cls.SECRET_PATTERNS:
            masked = re.sub(pattern, "[REDACTED_SECRET_KEY]", masked)
        return masked

    # ── In-memory token bucket for rate limiting ──
    _rate_buckets: dict[str, list[float]] = {}

    @classmethod
    def rate_limit_hook(cls, workspace_id: str, rate_limit_per_minute: int) -> bool:
        """
        Token bucket rate limiter. Returns True if request is allowed, False if blocked.
        """
        import time

        now = time.time()
        window = 60.0
        if workspace_id not in cls._rate_buckets:
            cls._rate_buckets[workspace_id] = []

        # Purge entries outside the window
        cls._rate_buckets[workspace_id] = [
            ts for ts in cls._rate_buckets[workspace_id] if now - ts < window
        ]

        if len(cls._rate_buckets[workspace_id]) >= rate_limit_per_minute:
            logger.warning(f"Rate limit exceeded for workspace '{workspace_id}'")
            return False

        cls._rate_buckets[workspace_id].append(now)
        return True

    @classmethod
    def validate_sql_injection(cls, text: str) -> bool:
        """Check for common SQL injection patterns."""
        sql_patterns = [
            r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER)\s+",
            r"'\s*OR\s+'1'\s*=\s*'1",
            r"UNION\s+SELECT",
            r"--\s*$",
        ]
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True

    @classmethod
    def validate_xss(cls, text: str) -> bool:
        """Check for common XSS attack patterns."""
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
        ]
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True
