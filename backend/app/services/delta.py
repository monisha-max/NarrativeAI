"""Delta Engine — persistent narrative memory and change detection."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session
from app.models.dossier import Dossier, DossierEvent
from app.models.user import FollowedDossier, UserSession
from app.services.redis import redis_service
from app.services.claude import claude_service


class DeltaEngine:
    """Computes what changed since a user's last visit to a dossier."""

    async def get_delta(self, user_id: str, dossier_slug: str) -> dict:
        """Get delta (what changed) for a user's followed dossier."""

        async with async_session() as db:
            # Get dossier
            dossier_result = await db.execute(
                select(Dossier).where(Dossier.slug == dossier_slug)
            )
            dossier = dossier_result.scalar_one_or_none()
            if not dossier:
                return {"error": "Dossier not found"}

            # Get user's last session state from Redis (fast) or DB (fallback)
            session_state = await redis_service.get_session_state(user_id, str(dossier.id))

            last_read_at = None
            read_event_ids = set()

            if session_state:
                last_read_at = datetime.fromisoformat(session_state.get("last_read_at", ""))
                read_event_ids = set(session_state.get("read_event_ids", []))
            else:
                # Check database
                session_result = await db.execute(
                    select(UserSession).where(
                        UserSession.user_id == uuid.UUID(user_id),
                        UserSession.dossier_id == dossier.id,
                    )
                )
                session = session_result.scalar_one_or_none()
                if session:
                    last_read_at = session.last_read_at
                    read_event_ids = set(session.read_event_ids.get("ids", [])) if session.read_event_ids else set()

            # Get all events for this dossier
            events_result = await db.execute(
                select(DossierEvent)
                .where(DossierEvent.dossier_id == dossier.id)
                .order_by(DossierEvent.occurred_at.desc())
            )
            all_events = events_result.scalars().all()

            # Determine new events
            if last_read_at:
                new_events = [
                    e for e in all_events
                    if e.occurred_at > last_read_at or str(e.id) not in read_event_ids
                ]
            else:
                new_events = list(all_events)  # First visit — everything is new

            # Compute sentiment shift
            sentiment_shift = self._compute_sentiment_shift(all_events, last_read_at)

            # Detect new entities
            old_entities = set()
            new_entities_set = set()
            for event in all_events:
                if event.entities_involved:
                    if last_read_at and event.occurred_at <= last_read_at:
                        old_entities.update(event.entities_involved)
                    else:
                        new_entities_set.update(event.entities_involved or [])

            new_entities = list(new_entities_set - old_entities)

        # Generate change summary using LLM
        change_summary = ""
        if new_events:
            change_summary = await self._generate_change_summary(
                dossier.title,
                [{"title": e.title, "summary": e.summary, "event_type": e.event_type}
                 for e in new_events[:10]],
            )

        # Build delta card
        delta = {
            "dossier_slug": dossier_slug,
            "dossier_title": dossier.title,
            "new_events_count": len(new_events),
            "change_summary": change_summary,
            "sentiment_shift": sentiment_shift,
            "new_entities": new_entities[:10],
            "predictions_tested": [],  # TODO: Compare predictions vs outcomes
            "phase_change": False,  # TODO: Check archetype phase
            "velocity_change": None,
            "ripple_alerts": [],  # TODO: Pull from RippleAlert table
            "significance_score": self._compute_significance(new_events, sentiment_shift),
            "last_checked": last_read_at.isoformat() if last_read_at else None,
            "new_events": [
                {
                    "id": str(e.id),
                    "title": e.title,
                    "summary": e.summary,
                    "event_type": e.event_type,
                    "occurred_at": e.occurred_at.isoformat(),
                }
                for e in new_events[:20]
            ],
        }

        # Update session state
        now = datetime.now(timezone.utc)
        all_event_ids = [str(e.id) for e in all_events]
        await redis_service.set_session_state(user_id, str(dossier.id) if dossier else "", {
            "last_read_at": now.isoformat(),
            "read_event_ids": all_event_ids,
        })

        return delta

    async def get_all_deltas(self, user_id: str) -> dict:
        """Get delta cards for all followed dossiers."""
        async with async_session() as db:
            follows_result = await db.execute(
                select(FollowedDossier).where(FollowedDossier.user_id == uuid.UUID(user_id))
            )
            follows = follows_result.scalars().all()

        cards = []
        for follow in follows:
            dossier_result = await db.execute(
                select(Dossier).where(Dossier.id == follow.dossier_id)
            )
            dossier = dossier_result.scalar_one_or_none()
            if dossier:
                delta = await self.get_delta(user_id, dossier.slug)
                cards.append(delta)

        # Sort by significance
        cards.sort(key=lambda c: c.get("significance_score", 0), reverse=True)

        # Generate 60-second summary
        sixty_second = None
        if cards:
            sixty_second = await self._generate_sixty_second(cards)

        return {
            "cards": cards,
            "sixty_second_summary": sixty_second,
        }

    def _compute_sentiment_shift(self, events: list, last_read_at: datetime | None) -> dict | None:
        """Compute how sentiment shifted since last visit."""
        if not last_read_at or not events:
            return None

        old_sentiments = []
        new_sentiments = []

        for event in events:
            if event.sentiment_scores:
                if event.occurred_at <= last_read_at:
                    old_sentiments.append(event.sentiment_scores)
                else:
                    new_sentiments.append(event.sentiment_scores)

        if not old_sentiments or not new_sentiments:
            return None

        def avg_sentiment(sentiments: list[dict]) -> dict:
            keys = ["market_confidence", "regulatory_heat", "media_tone", "stakeholder_sentiment"]
            return {
                k: sum(s.get(k, 0) for s in sentiments) / len(sentiments)
                for k in keys
            }

        old_avg = avg_sentiment(old_sentiments)
        new_avg = avg_sentiment(new_sentiments)

        return {
            k: round(new_avg[k] - old_avg[k], 3)
            for k in old_avg
        }

    def _compute_significance(self, new_events: list, sentiment_shift: dict | None) -> float:
        """Compute significance score for a delta card (0-1)."""
        score = 0.0

        # More new events = more significant
        score += min(len(new_events) / 10.0, 0.3)

        # Large sentiment shifts are significant
        if sentiment_shift:
            max_shift = max(abs(v) for v in sentiment_shift.values())
            score += min(max_shift * 2, 0.3)

        # Events with high market impact
        for event in new_events[:5]:
            if hasattr(event, 'market_impact') and event.market_impact:
                score += min(abs(event.market_impact) * 0.1, 0.2)

        # Regulatory events are always significant
        regulatory_count = sum(1 for e in new_events if hasattr(e, 'event_type') and e.event_type == "regulatory")
        score += min(regulatory_count * 0.1, 0.2)

        return min(score, 1.0)

    async def _generate_change_summary(self, dossier_title: str, events: list[dict]) -> str:
        """Generate a natural language summary of changes."""
        events_text = "\n".join(f"- {e['title']}: {e['summary']}" for e in events[:5])

        prompt = f"""The "{dossier_title}" story has {len(events)} new developments:

{events_text}

Write a 2-3 sentence summary of what changed. Be concise and highlight the most significant developments. Focus on what the reader needs to know."""

        try:
            return await claude_service.complete(
                system_prompt="You are a concise business news summarizer. Write in present tense. No filler words.",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
        except Exception:
            if events:
                return f"{len(events)} new developments. Latest: {events[0].get('title', '')}"
            return "No new developments."

    async def _generate_sixty_second(self, cards: list[dict]) -> dict:
        """Generate the 60-second briefing from all delta cards."""
        summaries = []
        for card in cards[:5]:
            summaries.append(f"- {card['dossier_title']}: {card['change_summary']}")

        prompt = f"""Based on these story updates:

{chr(10).join(summaries)}

Produce exactly three things:
1. most_important_change: The single most significant development across all stories (1 sentence)
2. biggest_risk: The biggest risk or uncertainty right now (1 sentence)
3. actionable_insight: One thing the reader should think about or act on today (1 sentence)

Return as JSON. Be ruthlessly concise."""

        try:
            return await claude_service.complete_json(
                system_prompt="You are a senior business intelligence analyst. Be extremely concise.",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
        except Exception:
            return {
                "most_important_change": cards[0].get("change_summary", "") if cards else "",
                "biggest_risk": "Check individual dossiers for risk assessment",
                "actionable_insight": "Review your followed stories for detailed updates",
            }


delta_engine = DeltaEngine()
