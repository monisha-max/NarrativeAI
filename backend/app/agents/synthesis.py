import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.prompts.synthesis import (
    BRIEFING_SYSTEM_PROMPT,
    CONSEQUENCE_SYSTEM_PROMPT,
    TIMELINE_SYSTEM_PROMPT,
)
from app.db.session import async_session
from app.models.article import Article
from app.models.dossier import Dossier, DossierEvent
from app.services.claude import claude_service
from app.services.fog import calculate_fog_density
from app.services.sentiment import compute_sentiment


class SynthesisAgent(BaseAgent):
    """Constructs timelines, sentiment arcs, narrative layers, fog calculations, claims tracking."""

    name = "synthesis"

    async def execute(self, context: AgentContext) -> AgentResult:
        dossier_id = context.dossier_id
        self.logger.info("synthesis.start", dossier_id=dossier_id)

        if not dossier_id:
            return AgentResult(
                agent_name=self.name, success=False, error="No dossier_id provided"
            )

        async with async_session() as db:
            # Load articles for this dossier
            result = await db.execute(
                select(Article)
                .where(Article.dossier_id == uuid.UUID(dossier_id))
                .order_by(Article.published_at)
            )
            articles = result.scalars().all()

            if not articles:
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    data={"timeline_events": [], "sentiment_arc": [], "claims_vs_facts": [], "fog_data": []},
                )

            self.logger.info("synthesis.articles_loaded", count=len(articles))

            # Phase 1: Extract timeline events using Claude
            timeline_events = await self._build_timeline(articles, context.query or "")

            # Phase 2: Store events in database
            stored_events = []
            for event_data in timeline_events:
                # Check for duplicate events
                existing = await db.execute(
                    select(DossierEvent).where(
                        DossierEvent.dossier_id == uuid.UUID(dossier_id),
                        DossierEvent.title == event_data.get("title"),
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                occurred_at = self._parse_event_date(event_data.get("occurred_at"))

                # Calculate fog density
                source_count = event_data.get("source_count", 1)
                fog_density = calculate_fog_density(
                    source_count=source_count,
                    source_diversity=min(source_count, 5),
                    has_official_source=event_data.get("has_official_source", False),
                    has_conflicting_reports=event_data.get("has_conflicting_reports", False),
                )

                sentiment = event_data.get("sentiment_scores", compute_sentiment(""))

                event = DossierEvent(
                    dossier_id=uuid.UUID(dossier_id),
                    event_type=event_data.get("event_type", "corporate"),
                    title=event_data.get("title", "Unknown event"),
                    summary=event_data.get("summary", ""),
                    occurred_at=occurred_at,
                    entities_involved=event_data.get("entities_involved", []),
                    sentiment_scores=sentiment,
                    market_impact=event_data.get("market_impact"),
                    fog_density=fog_density,
                )
                db.add(event)
                await db.flush()

                stored_events.append({
                    "id": str(event.id),
                    "title": event.title,
                    "summary": event.summary,
                    "event_type": event.event_type,
                    "occurred_at": occurred_at.isoformat(),
                    "entities_involved": event.entities_involved,
                    "sentiment_scores": sentiment,
                    "fog_density": fog_density,
                })

            # Phase 3: Build claims vs facts
            claims_vs_facts = await self._extract_claims(articles, context.query or "")

            # Phase 4: Compute sentiment arc
            sentiment_arc = self._compute_sentiment_arc(stored_events)

            # Phase 5: Calculate fog data for timeline
            fog_data = [
                {
                    "event_id": e["id"],
                    "occurred_at": e["occurred_at"],
                    "fog_density": e["fog_density"],
                }
                for e in stored_events
            ]

            # Phase 6: Generate narrative summary
            narrative = await self._generate_narrative(articles, stored_events, context.query or "")

            # Phase 7: Build consequence map
            consequence_map = await self._build_consequence_map(stored_events, context.query or "")

            # Update dossier metadata
            dossier = await db.get(Dossier, uuid.UUID(dossier_id))
            if dossier:
                dossier.article_count = len(articles)
                # Calculate velocity from event frequency
                dossier.velocity = self._calculate_velocity(stored_events)

            await db.commit()

        self.logger.info(
            "synthesis.complete",
            events=len(stored_events),
            claims=len(claims_vs_facts),
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "timeline_events": stored_events,
                "sentiment_arc": sentiment_arc,
                "claims_vs_facts": claims_vs_facts,
                "fog_data": fog_data,
                "narrative": narrative,
                "consequence_map": consequence_map,
            },
        )

    async def _build_timeline(self, articles: list[Article], query: str) -> list[dict]:
        """Use Claude to extract key timeline events from articles."""
        # Build article summaries for context
        article_texts = []
        for i, article in enumerate(articles[:80]):  # Limit to avoid token overflow
            article_texts.append(
                f"[Article {i+1}] {article.title} ({article.published_at.strftime('%Y-%m-%d') if article.published_at else 'unknown date'})\n"
                f"{article.content[:800]}"
            )

        articles_context = "\n\n---\n\n".join(article_texts)

        prompt = f"""Analyze these {len(article_texts)} articles about "{query}" and extract the key timeline events.

{articles_context}

Extract 15-30 major events. For each event, provide JSON with:
- title: concise event title (max 100 chars)
- summary: 2-3 sentence description
- event_type: one of [corporate, regulatory, financial, management, market, legal]
- occurred_at: ISO date (YYYY-MM-DD)
- entities_involved: list of entity names
- sentiment_scores: {{market_confidence: float (-1 to 1), regulatory_heat: float (0 to 1), media_tone: float (-1 to 1), stakeholder_sentiment: float (-1 to 1)}}
- market_impact: float (-1 to 1, negative = bad for stock, positive = good)
- source_count: estimated number of independent sources covering this event
- has_official_source: boolean (is there an official filing/statement?)
- has_conflicting_reports: boolean

Return a JSON array of events sorted chronologically."""

        try:
            events = await claude_service.complete_json(
                system_prompt=TIMELINE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
            )
            if isinstance(events, list):
                return events
            elif isinstance(events, dict) and "events" in events:
                return events["events"]
            return []
        except Exception as e:
            self.logger.error("synthesis.timeline.error", error=str(e))
            return []

    async def _extract_claims(self, articles: list[Article], query: str) -> list[dict]:
        """Extract claims vs confirmed facts from articles."""
        # Sample recent articles for claims extraction
        recent_articles = articles[-20:]
        article_texts = "\n\n".join(
            f"[{a.published_at.strftime('%Y-%m-%d') if a.published_at else '?'}] {a.title}: {a.content[:500]}"
            for a in recent_articles
        )

        prompt = f"""Analyze these articles about "{query}" and extract claims vs confirmed facts.

{article_texts}

For each claim, provide JSON with:
- claim: the assertion made
- status: one of [confirmed, invalidated, unverified, partially_confirmed]
- detail: evidence for the current status
- source: who made the claim
- date_claimed: when the claim was first made (YYYY-MM-DD)
- date_resolved: when it was confirmed/invalidated (YYYY-MM-DD or null)

Return a JSON array of 5-15 significant claims."""

        try:
            result = await claude_service.complete_json(
                system_prompt="You are an investigative journalist tracking claims and their outcomes in Indian business news. Be precise about what is confirmed vs unverified.",
                messages=[{"role": "user", "content": prompt}],
            )
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "claims" in result:
                return result["claims"]
            return []
        except Exception as e:
            self.logger.warning("synthesis.claims.error", error=str(e))
            return []

    def _compute_sentiment_arc(self, events: list[dict]) -> list[dict]:
        """Compute the sentiment arc from event data."""
        arc = []
        for event in events:
            scores = event.get("sentiment_scores")
            if scores:
                arc.append({
                    "date": event["occurred_at"],
                    "market_confidence": scores.get("market_confidence", 0),
                    "regulatory_heat": scores.get("regulatory_heat", 0),
                    "media_tone": scores.get("media_tone", 0),
                    "stakeholder_sentiment": scores.get("stakeholder_sentiment", 0),
                })
        return arc

    async def _generate_narrative(self, articles: list[Article], events: list[dict], query: str) -> dict:
        """Generate a narrative synthesis of the story."""
        events_text = "\n".join(
            f"- [{e['occurred_at']}] {e['title']}: {e['summary']}" for e in events[:20]
        )

        prompt = f"""Based on these key events in the "{query}" story:

{events_text}

Generate:
1. executive_summary: 3-4 sentence overview of the complete story arc
2. current_state: 2-3 sentences about where things stand now
3. key_players: list of the 5 most important entities and their roles
4. unresolved_questions: 3-5 questions that remain unanswered
5. narrative_phase: which phase the story appears to be in (early, developing, climax, resolution, aftermath)

Return as JSON."""

        try:
            return await claude_service.complete_json(
                system_prompt=BRIEFING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            self.logger.warning("synthesis.narrative.error", error=str(e))
            return {"executive_summary": "", "current_state": "", "key_players": [], "unresolved_questions": []}

    async def _build_consequence_map(self, events: list[dict], query: str) -> dict:
        """Build a who gains/who loses consequence map."""
        if not events:
            return {}

        recent_events = events[-5:]
        events_text = "\n".join(f"- {e['title']}: {e['summary']}" for e in recent_events)

        prompt = f"""Based on the latest developments in the "{query}" story:

{events_text}

Produce a consequence analysis:
1. who_gains: list of {{entity, reason}} — who benefits from recent developments
2. who_loses: list of {{entity, reason}} — who is harmed
3. sector_impact: list of {{sector, first_order_effect, second_order_effect}}
4. numbers_to_watch: list of specific metrics to monitor
5. scenarios: list of {{scenario, probability, trigger, impact}}

Return as JSON."""

        try:
            return await claude_service.complete_json(
                system_prompt=CONSEQUENCE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            self.logger.warning("synthesis.consequence.error", error=str(e))
            return {}

    def _calculate_velocity(self, events: list[dict]) -> str:
        """Calculate narrative velocity from event frequency."""
        if len(events) < 2:
            return "slow"

        # Calculate events per month
        dates = sorted([datetime.fromisoformat(e["occurred_at"]) for e in events])
        span_days = (dates[-1] - dates[0]).days
        if span_days == 0:
            return "crisis"

        events_per_month = (len(events) / span_days) * 30

        if events_per_month > 15:
            return "crisis"
        elif events_per_month > 4:
            return "rapid"
        elif events_per_month > 1:
            return "moderate"
        return "slow"

    def _parse_event_date(self, date_str: str | None) -> datetime:
        """Parse event date string."""
        if not date_str:
            return datetime.now(timezone.utc)
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, AttributeError):
            return datetime.now(timezone.utc)
