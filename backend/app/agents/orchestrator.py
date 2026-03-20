import asyncio
import uuid
from typing import AsyncGenerator

from sqlalchemy import select

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.ingestion import IngestionAgent
from app.agents.entity import EntityAgent
from app.agents.synthesis import SynthesisAgent
from app.agents.archetype import ArchetypeAgent
from app.agents.contrarian import ContrarianAgent
from app.agents.ripple import RippleAgent
from app.db.session import async_session
from app.models.dossier import Dossier


class OrchestratorAgent(BaseAgent):
    """Coordinates the full agent pipeline for dossier building and updates."""

    name = "orchestrator"

    def __init__(self):
        super().__init__()
        self.ingestion = IngestionAgent()
        self.entity = EntityAgent()
        self.synthesis = SynthesisAgent()
        self.archetype = ArchetypeAgent()
        self.contrarian = ContrarianAgent()
        self.ripple = RippleAgent()

    async def execute(self, context: AgentContext) -> AgentResult:
        results: dict[str, AgentResult] = {}

        # Ensure dossier exists
        dossier_id = context.dossier_id
        if not dossier_id and context.query:
            dossier_id = await self._ensure_dossier(context.query, context.data.get("dossier_slug"))
            context.dossier_id = dossier_id
            context.data["dossier_slug"] = context.data.get("dossier_slug") or self._slugify(context.query)

        # Phase 1: Ingestion — fetch new articles
        self.logger.info("orchestrator.phase1.ingestion", query=context.query)
        ingestion_result = await self.ingestion.run(context)
        results["ingestion"] = ingestion_result

        if not ingestion_result.success:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Ingestion failed: {ingestion_result.error}",
                data={"partial_results": {k: v.data for k, v in results.items()}},
            )

        # Phase 2: Entity extraction (depends on ingestion)
        self.logger.info("orchestrator.phase2.entity")
        context.parent_results = results
        entity_result = await self.entity.run(context)
        results["entity"] = entity_result

        # Phase 3: Parallel — Synthesis, Archetype, Contrarian, Ripple
        self.logger.info("orchestrator.phase3.parallel")
        context.parent_results = results

        parallel_results = await asyncio.gather(
            self.synthesis.run(context),
            self.archetype.run(context),
            self.contrarian.run(context),
            self.ripple.run(context),
            return_exceptions=True,
        )

        agent_names = ["synthesis", "archetype", "contrarian", "ripple"]
        for name, result in zip(agent_names, parallel_results):
            if isinstance(result, Exception):
                self.logger.error("orchestrator.agent.exception", agent=name, error=str(result))
                results[name] = AgentResult(
                    agent_name=name, success=False, error=str(result)
                )
            else:
                results[name] = result

        # Compile final output
        successful = {k: v.data for k, v in results.items() if v.success}
        failed = {k: v.error for k, v in results.items() if not v.success}

        self.logger.info(
            "orchestrator.complete",
            successful_agents=list(successful.keys()),
            failed_agents=list(failed.keys()),
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "dossier_id": dossier_id,
                "results": successful,
                "errors": failed,
                "summary": {
                    "articles_ingested": results.get("ingestion", AgentResult(agent_name="", success=False)).data.get("articles_new", 0),
                    "entities_found": results.get("entity", AgentResult(agent_name="", success=False)).data.get("entities_extracted", 0),
                    "timeline_events": len(results.get("synthesis", AgentResult(agent_name="", success=False)).data.get("timeline_events", [])),
                    "archetype_detected": results.get("archetype", AgentResult(agent_name="", success=False)).data.get("archetype"),
                    "ripple_connections": len(results.get("ripple", AgentResult(agent_name="", success=False)).data.get("ripple_connections", [])),
                },
            },
            metadata={
                "agent_durations": {k: v.duration_ms for k, v in results.items()},
            },
        )

    async def execute_progressive(self, context: AgentContext) -> AsyncGenerator[dict, None]:
        """Execute the pipeline with progressive rendering — yields status updates."""

        # Ensure dossier exists
        if not context.dossier_id and context.query:
            context.dossier_id = await self._ensure_dossier(
                context.query, context.data.get("dossier_slug")
            )
            context.data["dossier_slug"] = context.data.get("dossier_slug") or self._slugify(context.query)

        yield {"type": "status", "phase": "ingestion", "message": "Fetching articles..."}

        # Phase 1: Ingestion
        ingestion_result = await self.ingestion.run(context)
        context.parent_results = {"ingestion": ingestion_result}

        yield {
            "type": "ingestion_complete",
            "success": ingestion_result.success,
            "articles_found": ingestion_result.data.get("articles_found", 0),
            "articles_new": ingestion_result.data.get("articles_new", 0),
        }

        if not ingestion_result.success:
            yield {"type": "error", "message": f"Ingestion failed: {ingestion_result.error}"}
            return

        # Phase 2: Entity extraction
        yield {"type": "status", "phase": "entity", "message": "Extracting entities..."}
        entity_result = await self.entity.run(context)
        context.parent_results["entity"] = entity_result

        yield {
            "type": "entities_ready",
            "success": entity_result.success,
            "entities": entity_result.data.get("entities", []),
            "relationships": entity_result.data.get("relationships_found", 0),
        }

        # Phase 3: Parallel processing
        yield {"type": "status", "phase": "analysis", "message": "Analyzing narrative..."}

        # Run synthesis first (other agents may need its output)
        synthesis_result = await self.synthesis.run(context)
        context.parent_results["synthesis"] = synthesis_result

        yield {
            "type": "timeline_ready",
            "success": synthesis_result.success,
            "events": synthesis_result.data.get("timeline_events", []),
            "fog_data": synthesis_result.data.get("fog_data", []),
            "sentiment_arc": synthesis_result.data.get("sentiment_arc", []),
            "claims_vs_facts": synthesis_result.data.get("claims_vs_facts", []),
        }

        # Run remaining agents in parallel
        yield {"type": "status", "phase": "deep_analysis", "message": "Running deep analysis..."}

        archetype_task = asyncio.create_task(self.archetype.run(context))
        contrarian_task = asyncio.create_task(self.contrarian.run(context))
        ripple_task = asyncio.create_task(self.ripple.run(context))

        archetype_result = await archetype_task
        yield {
            "type": "archetype_ready",
            "success": archetype_result.success,
            "data": archetype_result.data,
        }

        contrarian_result = await contrarian_task
        yield {
            "type": "contrarian_ready",
            "success": contrarian_result.success,
            "data": contrarian_result.data,
        }

        ripple_result = await ripple_task
        yield {
            "type": "ripple_ready",
            "success": ripple_result.success,
            "data": ripple_result.data,
        }

        # Final summary
        yield {
            "type": "pipeline_complete",
            "dossier_id": context.dossier_id,
            "summary": {
                "articles_ingested": ingestion_result.data.get("articles_new", 0),
                "entities_found": entity_result.data.get("entities_extracted", 0),
                "timeline_events": len(synthesis_result.data.get("timeline_events", [])),
                "archetype_detected": archetype_result.data.get("archetype"),
                "ripple_connections": len(ripple_result.data.get("ripple_connections", [])),
            },
        }

    async def _ensure_dossier(self, query: str, slug: str | None = None) -> str:
        """Create a dossier if it doesn't exist, return its ID."""
        slug = slug or self._slugify(query)

        async with async_session() as db:
            result = await db.execute(select(Dossier).where(Dossier.slug == slug))
            dossier = result.scalar_one_or_none()

            if not dossier:
                dossier = Dossier(
                    title=query,
                    slug=slug,
                    description=f"Living dossier tracking: {query}",
                    status="active",
                )
                db.add(dossier)
                await db.commit()
                await db.refresh(dossier)

            return str(dossier.id)

    def _slugify(self, text: str) -> str:
        """Create a URL-safe slug from text."""
        import re
        slug = text.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug[:255]
