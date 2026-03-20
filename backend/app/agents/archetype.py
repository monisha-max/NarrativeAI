import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.prompts.archetype import ARCHETYPE_SYSTEM_PROMPT, SILENCE_DETECTION_PROMPT
from app.db.session import async_session
from app.models.archetype import Archetype, StoryDNA
from app.models.dossier import Dossier, DossierEvent
from app.services.claude import claude_service
from app.services.silence import calculate_silence_baseline, detect_silence


ARCHETYPE_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "archetypes"


class ArchetypeAgent(BaseAgent):
    """Fingerprints story DNA, detects current phase, generates predictions, checks silence."""

    name = "archetype"

    async def execute(self, context: AgentContext) -> AgentResult:
        dossier_id = context.dossier_id
        self.logger.info("archetype.start", dossier_id=dossier_id)

        if not dossier_id:
            return AgentResult(
                agent_name=self.name, success=False, error="No dossier_id provided"
            )

        async with async_session() as db:
            # Load dossier events
            result = await db.execute(
                select(DossierEvent)
                .where(DossierEvent.dossier_id == uuid.UUID(dossier_id))
                .order_by(DossierEvent.occurred_at)
            )
            events = result.scalars().all()

            if not events:
                # Try to use synthesis results from parent
                synthesis_data = context.parent_results.get("synthesis")
                if synthesis_data and synthesis_data.success:
                    events_data = synthesis_data.data.get("timeline_events", [])
                else:
                    return AgentResult(
                        agent_name=self.name, success=True,
                        data={"archetype": None, "message": "No events to analyze"},
                    )
            else:
                events_data = [
                    {
                        "title": e.title,
                        "summary": e.summary,
                        "event_type": e.event_type,
                        "occurred_at": e.occurred_at.isoformat() if e.occurred_at else "",
                        "entities_involved": e.entities_involved or [],
                    }
                    for e in events
                ]

            # Load archetype library
            archetypes = await self._load_archetypes(db)

            # Phase 1: Fingerprint the story against archetypes
            archetype_match = await self._fingerprint_story(events_data, archetypes, context.query or "")

            if not archetype_match:
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    data={
                        "archetype": "Novel Pattern",
                        "current_phase": None,
                        "confidence": 0.0,
                        "prediction": None,
                        "silence_alert": None,
                        "message": "No historical archetype matched. This appears to be a novel pattern.",
                    },
                )

            # Phase 2: Detect silence anomalies
            event_dates = []
            for e in events_data:
                try:
                    dt = datetime.fromisoformat(e["occurred_at"].replace("Z", "+00:00"))
                    event_dates.append(dt)
                except (ValueError, KeyError):
                    pass

            silence_alert = None
            if event_dates:
                baseline = calculate_silence_baseline(event_dates, archetype_match.get("archetype_slug"))
                silence_alert = detect_silence(event_dates, baseline, archetype_match.get("archetype_slug"))

                # Enhance silence alert with LLM analysis
                if silence_alert:
                    silence_alert = await self._analyze_silence(
                        silence_alert, events_data, archetype_match, context.query or ""
                    )

            # Phase 3: Store Story DNA in database
            archetype_slug = archetype_match.get("archetype_slug", "")
            archetype_record = await db.execute(
                select(Archetype).where(Archetype.slug == archetype_slug)
            )
            archetype_obj = archetype_record.scalar_one_or_none()

            if archetype_obj:
                # Update or create StoryDNA
                existing_dna = await db.execute(
                    select(StoryDNA).where(StoryDNA.dossier_id == uuid.UUID(dossier_id))
                )
                dna = existing_dna.scalar_one_or_none()

                prediction = archetype_match.get("prediction")
                current_phase = archetype_match.get("current_phase", 1)
                confidence = archetype_match.get("confidence", 0.5)

                if dna:
                    dna.archetype_id = archetype_obj.id
                    dna.current_phase = current_phase
                    dna.confidence = confidence
                    dna.phase_prediction = prediction
                    dna.silence_baseline_days = 1.0 / baseline if baseline > 0 else None
                    dna.last_silence_check = silence_alert
                else:
                    dna = StoryDNA(
                        dossier_id=uuid.UUID(dossier_id),
                        archetype_id=archetype_obj.id,
                        current_phase=current_phase,
                        confidence=confidence,
                        phase_prediction=prediction,
                        silence_baseline_days=1.0 / baseline if baseline > 0 else None,
                        last_silence_check=silence_alert,
                    )
                    db.add(dna)

            await db.commit()

        self.logger.info(
            "archetype.complete",
            archetype=archetype_match.get("archetype_name"),
            phase=archetype_match.get("current_phase"),
            confidence=archetype_match.get("confidence"),
            silence=silence_alert is not None,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "archetype": archetype_match.get("archetype_name"),
                "archetype_slug": archetype_match.get("archetype_slug"),
                "current_phase": archetype_match.get("current_phase"),
                "phase_name": archetype_match.get("phase_name"),
                "confidence": archetype_match.get("confidence"),
                "prediction": archetype_match.get("prediction"),
                "historical_parallels": archetype_match.get("historical_parallels", []),
                "silence_alert": silence_alert,
            },
        )

    async def _load_archetypes(self, db: AsyncSession) -> list[dict]:
        """Load archetype library from database or JSON files."""
        result = await db.execute(
            select(Archetype).options(selectinload(Archetype.phases))
        )
        archetypes = result.scalars().all()

        if archetypes:
            return [
                {
                    "name": a.name,
                    "slug": a.slug,
                    "description": a.description,
                    "phases": [
                        {
                            "phase_number": p.phase_number,
                            "name": p.name,
                            "description": p.description,
                            "transition_indicators": p.transition_indicators or [],
                        }
                        for p in a.phases
                    ],
                    "reference_cases": a.reference_cases or [],
                }
                for a in archetypes
            ]

        # Fallback: load from JSON files
        archetype_list = []
        for json_file in ARCHETYPE_DATA_DIR.glob("*.json"):
            data = json.loads(json_file.read_text())
            archetype_list.append(data)
        return archetype_list

    async def _fingerprint_story(self, events: list[dict], archetypes: list[dict], query: str) -> dict | None:
        """Use Claude to match the story against archetypes and identify current phase."""
        events_text = "\n".join(
            f"- [{e.get('occurred_at', '?')}] ({e.get('event_type', '?')}) {e.get('title', '')}: {e.get('summary', '')}"
            for e in events[:30]
        )

        archetypes_text = ""
        for arch in archetypes:
            phases_text = "\n".join(
                f"    Phase {p['phase_number']}: {p['name']} — {p.get('description', '')[:100]}"
                for p in arch.get("phases", [])
            )
            archetypes_text += f"\n{arch['name']} ({arch['slug']}):\n  {arch['description'][:200]}\n  Reference cases: {', '.join(arch.get('reference_cases', []))}\n  Phases:\n{phases_text}\n"

        prompt = f"""Story: "{query}"

Timeline events:
{events_text}

Available Archetypes:
{archetypes_text}

Analyze the event sequence and determine:
1. archetype_name: which archetype best matches (or "Novel Pattern" if none fits)
2. archetype_slug: the slug of the matching archetype
3. current_phase: which phase number the story is currently in
4. phase_name: name of the current phase
5. confidence: 0.0 to 1.0 confidence in the match
6. reasoning: 2-3 sentences explaining why this archetype matches
7. prediction: {{next_phase: int, probability: float, estimated_days: int, trigger_events: [list of events to watch for]}}
8. historical_parallels: list of similar stories from reference cases and how they progressed

Return as JSON."""

        try:
            result = await claude_service.complete_json(
                system_prompt=ARCHETYPE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            if result.get("archetype_name") == "Novel Pattern":
                return None
            return result
        except Exception as e:
            self.logger.error("archetype.fingerprint.error", error=str(e))
            return None

    async def _analyze_silence(
        self, silence_alert: dict, events: list[dict], archetype_match: dict, query: str
    ) -> dict:
        """Enhance silence alert with LLM analysis of what silence might mean."""
        last_events = events[-5:]
        events_text = "\n".join(f"- {e.get('title', '')}" for e in last_events)

        prompt = f"""The story "{query}" has been silent for {silence_alert['days_silent']} days.
Normal publication rate: {silence_alert['baseline_rate']:.2f} events/day.
Expected events during silence: {silence_alert['expected_events']}.

Story archetype: {archetype_match.get('archetype_name', 'Unknown')}
Current phase: Phase {archetype_match.get('current_phase', '?')}

Last known events:
{events_text}

Analyze:
1. What might explain this silence?
2. In historical cases of this archetype, what typically follows this kind of silence?
3. What percentage of similar silence periods preceded major developments?
4. What should the reader be watching for?

Return JSON with: explanation, historical_precedent, probability_of_major_event (float), what_to_watch (list)."""

        try:
            analysis = await claude_service.complete_json(
                system_prompt=SILENCE_DETECTION_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            silence_alert.update(analysis)
        except Exception as e:
            self.logger.warning("archetype.silence_analysis.error", error=str(e))

        return silence_alert
