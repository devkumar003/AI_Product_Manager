import logging

from app.ai.core.llm_manager import LLMManager

logger = logging.getLogger("app.services.planning.context_compression")


class ContextCompressor:
    """
    Context Compressor utility. Semantically compresses conversations, documents,
    memories, and agent outputs to save token limits while preserving critical facts.
    """

    def __init__(self, llm_manager: LLMManager | None = None) -> None:
        self.llm = llm_manager or LLMManager()

    async def compress_text(self, text: str, target_summary_words: int = 300) -> str:
        """
        Compresses any raw text, document, or memory into a highly condensed version.
        """
        if not text or len(text) < 100:
            return text

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a context compression engine. Your task is to compress the provided text "
                    "semantically. Keep all critical facts, technical details, dates, tasks, decisions, "
                    f"and constraints, but remove fluff, verbose sentences, and repetition. Target length: ~{target_summary_words} words."
                ),
            },
            {"role": "user", "content": f"Please compress this text:\n\n{text}"},
        ]

        try:
            response = await self.llm.generate(messages, temperature=0.2)
            return response.content
        except Exception as e:
            logger.error(f"Failed to compress text: {str(e)}")
            # Return a simple truncation as fallback
            words = text.split()
            return (
                " ".join(words[:target_summary_words])
                + "... [Truncated due to compression failure]"
            )

    async def compress_messages(
        self, messages: list[dict[str, str]], target_turns: int = 4
    ) -> list[dict[str, str]]:
        """
        Compresses conversation history. Older turns are summarized, keeping only the most recent turns intact.
        """
        if len(messages) <= target_turns:
            return messages

        # Separate recent messages to keep intact, and older messages to compress
        intact_messages = messages[-target_turns:]
        older_messages = messages[:-target_turns]

        # Stringify older messages
        history_text = "\n".join(
            [f"{msg['role'].upper()}: {msg['content']}" for msg in older_messages]
        )

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are an assistant that summarizes conversational history. "
                    "Provide a concise summary of the key context, topics, decisions made, and technical details discussed in this chat history."
                ),
            },
            {
                "role": "user",
                "content": f"Summarize this conversation history:\n\n{history_text}",
            },
        ]

        try:
            summary_response = await self.llm.generate(prompt, temperature=0.2)
            summary_text = (
                f"[SYSTEM SUMMARY of older chat context]: {summary_response.content}"
            )
            return [{"role": "system", "content": summary_text}] + intact_messages
        except Exception as e:
            logger.error(f"Failed to compress message history: {str(e)}")
            # Fallback: just return the recent messages
            return intact_messages
