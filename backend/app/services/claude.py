import anthropic
import structlog

from app.config import settings

logger = structlog.get_logger()


class ClaudeService:
    """Wrapper around the Anthropic Claude API."""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"

    async def complete(
        self,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> str:
        """Send a completion request and return the text response."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                temperature=temperature,
            )
            return response.content[0].text
        except Exception as e:
            logger.error("claude.complete.error", error=str(e))
            raise

    async def stream(
        self,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ):
        """Stream a completion response, yielding text chunks."""
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                temperature=temperature,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error("claude.stream.error", error=str(e))
            raise

    async def complete_json(
        self,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> dict:
        """Send a completion request expecting JSON output."""
        import orjson

        text = await self.complete(
            system_prompt=system_prompt + "\n\nRespond with valid JSON only.",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.1,
        )
        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return orjson.loads(text)


claude_service = ClaudeService()
