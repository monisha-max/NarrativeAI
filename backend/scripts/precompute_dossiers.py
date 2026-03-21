"""Pre-compute demo dossiers — run archetype detection and cache results."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import async_session, engine
from app.models.base import Base
from app.models.dossier import Dossier
from app.models.archetype import Archetype, StoryDNA
from app.services.redis import redis_service
from app.agents.archetype import ArchetypeAgent
from app.agents.base import AgentContext


async def precompute():
    """Pre-compute archetype matching and cache dossier data for demo."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Get all active dossiers
        result = await db.execute(
            select(Dossier)
            .where(Dossier.status == "active")
            .options(selectinload(Dossier.events))
        )
        dossiers = result.scalars().all()

        if not dossiers:
            print("No dossiers found. Run seed_demo_dossiers.py first.")
            return

        archetype_agent = ArchetypeAgent()

        for dossier in dossiers:
            print(f"\n  Pre-computing: {dossier.title}...")

            # Run archetype detection
            context = AgentContext(
                dossier_id=str(dossier.id),
                query=dossier.title,
            )

            try:
                result = await archetype_agent.run(context)
                if result.success:
                    print(f"    Archetype: {result.data.get('archetype', 'None')}")
                    print(f"    Phase: {result.data.get('current_phase', '?')}")
                    print(f"    Confidence: {result.data.get('confidence', 0):.0%}")

                    if result.data.get("silence_alert"):
                        print(f"    Silence alert: {result.data['silence_alert'].get('days_silent', 0)} days")
                else:
                    print(f"    Archetype detection failed: {result.error}")
            except Exception as e:
                print(f"    Error: {e}")

            # Cache the dossier data in Redis for fast loading
            dossier_cache = {
                "id": str(dossier.id),
                "title": dossier.title,
                "slug": dossier.slug,
                "description": dossier.description,
                "status": dossier.status,
                "velocity": dossier.velocity,
                "article_count": dossier.article_count,
                "tags": dossier.tags,
                "events": [
                    {
                        "id": str(e.id),
                        "title": e.title,
                        "summary": e.summary,
                        "event_type": e.event_type,
                        "occurred_at": e.occurred_at.isoformat(),
                        "entities_involved": e.entities_involved,
                        "sentiment_scores": e.sentiment_scores,
                        "fog_density": e.fog_density,
                    }
                    for e in dossier.events
                ],
            }

            try:
                await redis_service.cache_dossier(dossier.slug, dossier_cache, ttl=86400 * 7)
                print(f"    Cached in Redis (7-day TTL)")
            except Exception as e:
                print(f"    Redis cache failed: {e}")
                # Save to disk as fallback
                cache_dir = Path(__file__).parent.parent / "data" / "cache"
                cache_dir.mkdir(exist_ok=True)
                (cache_dir / f"{dossier.slug}.json").write_text(
                    json.dumps(dossier_cache, default=str, indent=2)
                )
                print(f"    Saved to disk cache: data/cache/{dossier.slug}.json")

    print("\n  Pre-computation complete.")


if __name__ == "__main__":
    asyncio.run(precompute())
