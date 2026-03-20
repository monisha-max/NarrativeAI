import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.session import async_session
from app.models.dossier import Dossier, DossierEvent
from app.models.entity import Entity, EntityRelationship
from app.models.ripple import RippleAlert, RippleConnection
from app.services.claude import claude_service


class RippleAgent(BaseAgent):
    """Detects cross-story impact via shared entities, sectors, regulatory chains, financial links."""

    name = "ripple"

    async def execute(self, context: AgentContext) -> AgentResult:
        dossier_id = context.dossier_id
        self.logger.info("ripple.start", dossier_id=dossier_id)

        if not dossier_id:
            return AgentResult(
                agent_name=self.name, success=False, error="No dossier_id provided"
            )

        async with async_session() as db:
            # Load current dossier
            current_dossier = await db.get(Dossier, uuid.UUID(dossier_id))
            if not current_dossier:
                return AgentResult(
                    agent_name=self.name, success=True,
                    data={"ripple_connections": [], "ripple_alerts": []},
                )

            # Load all other active dossiers
            other_dossiers_result = await db.execute(
                select(Dossier).where(
                    Dossier.status == "active",
                    Dossier.id != uuid.UUID(dossier_id),
                )
            )
            other_dossiers = other_dossiers_result.scalars().all()

            if not other_dossiers:
                return AgentResult(
                    agent_name=self.name, success=True,
                    data={"ripple_connections": [], "ripple_alerts": [], "message": "No other dossiers to check ripples against"},
                )

            # Get current dossier's entities
            current_events_result = await db.execute(
                select(DossierEvent)
                .where(DossierEvent.dossier_id == uuid.UUID(dossier_id))
                .order_by(DossierEvent.occurred_at.desc())
                .limit(10)
            )
            current_events = current_events_result.scalars().all()

            current_entities = set()
            for event in current_events:
                if event.entities_involved:
                    current_entities.update(event.entities_involved)

            # Get current dossier's entity relationships
            current_rels_result = await db.execute(
                select(EntityRelationship).where(
                    EntityRelationship.dossier_id == uuid.UUID(dossier_id)
                )
            )
            current_rels = current_rels_result.scalars().all()

            current_entity_ids = set()
            for rel in current_rels:
                current_entity_ids.add(str(rel.source_entity_id))
                current_entity_ids.add(str(rel.target_entity_id))

            # Phase 1: Detect entity overlap with other dossiers
            connections = []
            for other_dossier in other_dossiers:
                overlap = await self._check_entity_overlap(db, dossier_id, str(other_dossier.id), current_entities)

                if overlap["shared_count"] > 0:
                    # Calculate connection strength
                    strength = min(overlap["shared_count"] / 5.0, 1.0)

                    # Check if connection already exists
                    existing = await db.execute(
                        select(RippleConnection).where(
                            RippleConnection.source_dossier_id == uuid.UUID(dossier_id),
                            RippleConnection.target_dossier_id == other_dossier.id,
                        )
                    )
                    existing_conn = existing.scalar_one_or_none()

                    if existing_conn:
                        existing_conn.strength = strength
                        existing_conn.shared_entities = {"entities": overlap["shared_entities"]}
                    else:
                        conn = RippleConnection(
                            source_dossier_id=uuid.UUID(dossier_id),
                            target_dossier_id=other_dossier.id,
                            connection_type=overlap["connection_type"],
                            strength=strength,
                            shared_entities={"entities": overlap["shared_entities"]},
                            description=f"Shared entities: {', '.join(overlap['shared_entities'][:5])}",
                        )
                        db.add(conn)

                    connections.append({
                        "target_dossier_id": str(other_dossier.id),
                        "target_dossier_title": other_dossier.title,
                        "target_dossier_slug": other_dossier.slug,
                        "connection_type": overlap["connection_type"],
                        "strength": strength,
                        "shared_entities": overlap["shared_entities"],
                    })

            # Phase 2: Generate ripple alerts for recent events
            alerts = []
            if connections and current_events:
                latest_event = current_events[0]
                for conn in connections:
                    if conn["strength"] >= 0.3:  # Only alert for significant connections
                        alert_data = await self._generate_ripple_alert(
                            current_dossier.title,
                            conn["target_dossier_title"],
                            latest_event.title,
                            latest_event.summary,
                            conn["shared_entities"],
                        )

                        if alert_data and alert_data.get("magnitude", 0) >= 0.3:
                            alert = RippleAlert(
                                source_dossier_id=uuid.UUID(dossier_id),
                                target_dossier_id=uuid.UUID(conn["target_dossier_id"]),
                                trigger_event_id=latest_event.id,
                                impact_description=alert_data.get("impact", "Potential cross-story impact detected"),
                                magnitude=alert_data.get("magnitude", 0.5),
                            )
                            db.add(alert)

                            alerts.append({
                                "target_dossier": conn["target_dossier_title"],
                                "impact": alert_data.get("impact"),
                                "magnitude": alert_data.get("magnitude"),
                                "mechanism": alert_data.get("mechanism"),
                            })

            await db.commit()

        self.logger.info(
            "ripple.complete",
            connections=len(connections),
            alerts=len(alerts),
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "ripple_connections": connections,
                "ripple_alerts": alerts,
            },
        )

    async def _check_entity_overlap(
        self, db: AsyncSession, current_dossier_id: str, other_dossier_id: str, current_entities: set[str]
    ) -> dict:
        """Check for shared entities between two dossiers."""
        other_events_result = await db.execute(
            select(DossierEvent)
            .where(DossierEvent.dossier_id == uuid.UUID(other_dossier_id))
        )
        other_events = other_events_result.scalars().all()

        other_entities = set()
        for event in other_events:
            if event.entities_involved:
                other_entities.update(event.entities_involved)

        shared = current_entities & other_entities

        # Determine connection type based on shared entities
        connection_type = "entity"
        shared_lower = {s.lower() for s in shared}
        if any(r in shared_lower for r in ["rbi", "sebi", "nclt", "nclat", "irdai"]):
            connection_type = "regulatory"
        elif any(s in shared_lower for s in ["nse", "bse", "sensex", "nifty"]):
            connection_type = "financial"

        return {
            "shared_count": len(shared),
            "shared_entities": list(shared),
            "connection_type": connection_type,
        }

    async def _generate_ripple_alert(
        self,
        source_dossier: str,
        target_dossier: str,
        event_title: str,
        event_summary: str,
        shared_entities: list[str],
    ) -> dict | None:
        """Generate a ripple alert for a cross-story impact."""
        prompt = f"""A new development in the "{source_dossier}" story may affect the "{target_dossier}" story.

New event: {event_title}
Details: {event_summary}
Shared entities: {', '.join(shared_entities[:5])}

Analyze:
1. impact: one-sentence description of how this development affects the "{target_dossier}" story
2. magnitude: float 0-1 (how significant is this cross-story impact?)
3. mechanism: how exactly does the impact propagate (shared entity, sector linkage, regulatory chain, financial linkage)?
4. urgency: high/medium/low

Only report genuine cross-story impacts. If the connection is superficial, set magnitude below 0.2.
Return as JSON."""

        try:
            return await claude_service.complete_json(
                system_prompt="You are an expert at identifying cross-story connections in Indian business news. Only flag genuine causal connections, not coincidental mentions.",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
            )
        except Exception as e:
            self.logger.warning("ripple.alert.error", error=str(e))
            return None
