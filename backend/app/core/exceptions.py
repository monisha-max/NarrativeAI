class NarrativeAIError(Exception):
    """Base exception for NarrativeAI."""
    pass


class DossierNotFoundError(NarrativeAIError):
    """Dossier not found."""
    pass


class AgentExecutionError(NarrativeAIError):
    """Agent failed to execute."""
    pass


class IngestionError(NarrativeAIError):
    """Article ingestion failed."""
    pass


class ArchetypeMatchError(NarrativeAIError):
    """No archetype match found."""
    pass
