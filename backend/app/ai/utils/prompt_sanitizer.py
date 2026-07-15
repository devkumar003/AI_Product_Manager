import re

def sanitize_prompt_input(text: str) -> str:
    """
    Sanitizes user input to prevent prompt injection by stripping instruction-override patterns.
    """
    if not text:
        return text
    
    # Common prompt injection override keywords / patterns
    injection_patterns = [
        "ignore previous",
        "ignore above",
        "system override",
        "override system",
        "you are now a",
        "you are no longer",
        "instead of",
        "new instructions",
        "do not follow",
        "ignore the instructions",
        "system prompt",
        "developer mode"
    ]
    
    sanitized = text
    for pattern in injection_patterns:
        # Case-insensitive replacement
        sanitized = re.sub(re.escape(pattern), "[REDACTED_OVERRIDE]", sanitized, flags=re.IGNORECASE)
    
    return sanitized
