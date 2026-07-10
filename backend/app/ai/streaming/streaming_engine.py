import asyncio
import json
import logging
from collections.abc import AsyncIterator

from app.ai.schemas import StreamingToken

logger = logging.getLogger("app.ai.streaming_engine")


class StreamingEngine:
    """
    Core engine managing LLM response streaming. Translates token iterators
    to HTTP SSE outputs, checking for timeouts, cancellation, and connection reconnects.
    """

    def __init__(self, token_timeout: float = 15.0) -> None:
        self.token_timeout = token_timeout

    async def sse_event_generator(
        self, token_iterator: AsyncIterator[StreamingToken]
    ) -> AsyncIterator[str]:
        """
        Consumes a StreamingToken iterator and yields formatted Server-Sent Event (SSE) strings.
        Protects against frozen model streams using a token-arrival timeout guard.
        """
        try:
            while True:
                # Wrap next token retrieval with timeout limit
                try:
                    token_task = asyncio.create_task(token_iterator.__anext__())
                    token = await asyncio.wait_for(
                        token_task, timeout=self.token_timeout
                    )
                except TimeoutError:
                    logger.error("Streaming token delivery timed out.")
                    yield f"data: {json.dumps({'error': 'Token delivery timeout', 'done': True})}\n\n"
                    break
                except StopAsyncIteration:
                    # Normal stream end
                    yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
                    break

                if token.error:
                    logger.error(f"Streaming token stream yielded error: {token.error}")
                    yield f"data: {json.dumps({'error': token.error, 'done': True})}\n\n"
                    break

                # Format token payload as SSE line
                payload = {"token": token.token, "done": token.done}
                yield f"data: {json.dumps(payload)}\n\n"

                if token.done:
                    break

        except asyncio.CancelledError:
            logger.info(
                "Streaming client disconnected. Cancelling upstream generator tasks."
            )
            # Yield connection-cut event to inform telemetry/routing
            yield f"data: {json.dumps({'error': 'Client disconnected', 'done': True})}\n\n"
            raise
        except Exception as e:
            logger.exception("Unexpected error in streaming engine generator loop.")
            yield f"data: {json.dumps({'error': f'Stream exception: {str(e)}', 'done': True})}\n\n"
