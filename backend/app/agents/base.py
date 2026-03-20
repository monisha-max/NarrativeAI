import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class AgentContext:
    """Input context for an agent execution."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dossier_id: str | None = None
    user_id: str | None = None
    query: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    parent_results: dict[str, "AgentResult"] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Output result from an agent execution."""

    agent_name: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base class for all NarrativeAI agents."""

    name: str = "base"
    max_retries: int = 3
    timeout: int = 60

    def __init__(self):
        self.logger = structlog.get_logger().bind(agent=self.name)

    async def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent with retry logic and timing."""
        start = time.monotonic()
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info("agent.execute.start", attempt=attempt, request_id=context.request_id)
                result = await self.execute(context)
                result.duration_ms = (time.monotonic() - start) * 1000
                self.logger.info(
                    "agent.execute.success",
                    duration_ms=result.duration_ms,
                    request_id=context.request_id,
                )
                return result
            except Exception as e:
                last_error = str(e)
                self.logger.warning(
                    "agent.execute.retry",
                    attempt=attempt,
                    error=last_error,
                    request_id=context.request_id,
                )
                if attempt == self.max_retries:
                    break

        duration = (time.monotonic() - start) * 1000
        self.logger.error("agent.execute.failed", error=last_error, request_id=context.request_id)
        return AgentResult(
            agent_name=self.name,
            success=False,
            error=last_error,
            duration_ms=duration,
        )

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Implement the agent's core logic. Override in subclasses."""
        ...
