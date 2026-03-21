import pytest


@pytest.fixture
def sample_context():
    from app.agents.base import AgentContext
    return AgentContext(
        dossier_id="test-dossier",
        query="Byju's crisis",
    )
