import json
import logging
import re
from typing import Any

logger = logging.getLogger("app.ai.utils.json_parser")


def extract_json_from_text(text: Any) -> Any:
    """
    Robustly extracts and parses JSON objects or arrays from raw LLM text outputs.
    Handles markdown code blocks, conversational filler before/after JSON, and nested structures.
    """
    if isinstance(text, (dict, list)):
        return text

    if not isinstance(text, str):
        raise ValueError(f"Expected string or JSON structure, got {type(text)}")

    cleaned = text.strip()

    # 1. Direct parse attempt
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown code fences if present
    if "```" in cleaned:
        # Match inside ```json ... ``` or ``` ... ```
        fence_pattern = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
        matches = fence_pattern.findall(cleaned)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

    # 3. Smart bracket/brace balancing extraction
    first_brace = cleaned.find("{")
    first_bracket = cleaned.find("[")

    start_idx = -1
    end_idx = -1

    if first_brace >= 0 and first_bracket >= 0:
        if first_brace < first_bracket:
            start_idx = first_brace
            end_idx = cleaned.rfind("}")
        else:
            start_idx = first_bracket
            end_idx = cleaned.rfind("]")
    elif first_brace >= 0:
        start_idx = first_brace
        end_idx = cleaned.rfind("}")
    elif first_bracket >= 0:
        start_idx = first_bracket
        end_idx = cleaned.rfind("]")

    if start_idx >= 0 and end_idx > start_idx:
        candidate = cleaned[start_idx : end_idx + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            # 4. Attempt basic trailing comma cleanup
            try:
                cleaned_candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
                return json.loads(cleaned_candidate)
            except json.JSONDecodeError:
                raise e

    raise ValueError(f"Could not extract valid JSON from LLM response: {cleaned[:200]}...")


async def generate_with_json_healing(
    llm_manager: Any,
    messages: list[dict[str, str]],
    config: dict[str, Any] | None = None,
    max_retries: int = 2,
) -> Any:
    """
    Executes an LLM generation call and extracts JSON. If a syntax decode error occurs,
    initiates an automated self-healing retry loop feeding the error line/col back to the LLM.
    """
    config = config or {}
    current_messages = list(messages)

    for attempt in range(max_retries + 1):
        try:
            res = await llm_manager.generate(messages=current_messages, **config)
            content = res.content if hasattr(res, "content") else str(res)
            return extract_json_from_text(content)
        except (json.JSONDecodeError, ValueError) as e:
            if attempt == max_retries:
                logger.error(f"JSON self-healing failed after {max_retries} retries: {str(e)}")
                raise e

            logger.warning(
                f"JSON decode failed on attempt {attempt + 1}: {str(e)}. Initiating self-healing repair prompt..."
            )
            # Add error feedback to message chain for repair
            content_val = res.content if 'res' in locals() and hasattr(res, "content") else ""
            current_messages.append({"role": "assistant", "content": content_val})
            current_messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Your previous response failed JSON syntax decoding with error: '{str(e)}'. "
                        "Please output ONLY valid JSON without markdown code blocks, filler text, or trailing commas."
                    ),
                }
            )
            # Lower temperature for deterministic repair
            config["temperature"] = min(config.get("temperature", 0.7), 0.1)
