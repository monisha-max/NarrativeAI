import pytest
from app.agents.orchestrator import OrchestratorAgent
from app.agents.base import AgentContext


@pytest.mark.asyncio
async def test_orchestrator_runs():
    orchestrator = OrchestratorAgent()
    context = AgentContext(query="test query")
    result = await orchestrator.run(context)
    assert result.agent_name == "orchestrator"
    assert result.success is True
