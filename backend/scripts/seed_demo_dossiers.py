"""Seed demo dossiers with pre-built events from corpus data."""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.db.session import async_session, engine
from app.models.base import Base
from app.models.dossier import Dossier, DossierEvent


CORPUS_FILE = Path(__file__).parent.parent / "data" / "corpus" / "demo_dossiers.json"


async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    data = json.loads(CORPUS_FILE.read_text())

    async with async_session() as session:
        for dossier_data in data:
            # Check if dossier already exists
            existing = await session.execute(
                select(Dossier).where(Dossier.slug == dossier_data["slug"])
            )
            if existing.scalar_one_or_none():
                print(f"  Skipping {dossier_data['title']} (already exists)")
                continue

            # Create dossier
            dossier = Dossier(
                title=dossier_data["title"],
                slug=dossier_data["slug"],
                description=dossier_data["description"],
                status="active",
                tags=dossier_data.get("tags"),
                article_count=len(dossier_data.get("events", [])) * 3,  # Estimated articles per event
            )

            # Calculate velocity
            events = dossier_data.get("events", [])
            if len(events) >= 2:
                dates = sorted([datetime.fromisoformat(e["occurred_at"]) for e in events])
                span_days = (dates[-1] - dates[0]).days
                if span_days > 0:
                    events_per_month = (len(events) / span_days) * 30
                    if events_per_month > 15:
                        dossier.velocity = "crisis"
                    elif events_per_month > 4:
                        dossier.velocity = "rapid"
                    elif events_per_month > 1:
                        dossier.velocity = "moderate"
                    else:
                        dossier.velocity = "slow"

            session.add(dossier)
            await session.flush()

            # Create events
            for event_data in events:
                occurred_at = datetime.fromisoformat(event_data["occurred_at"])
                if occurred_at.tzinfo is None:
                    occurred_at = occurred_at.replace(tzinfo=timezone.utc)

                event = DossierEvent(
                    dossier_id=dossier.id,
                    event_type=event_data["event_type"],
                    title=event_data["title"],
                    summary=event_data["summary"],
                    occurred_at=occurred_at,
                    entities_involved=event_data.get("entities_involved"),
                    sentiment_scores=event_data.get("sentiment_scores"),
                    market_impact=event_data.get("market_impact"),
                    fog_density=event_data.get("fog_density", 0.3),
                )
                session.add(event)

            print(f"  Seeded: {dossier_data['title']} ({len(events)} events)")

        await session.commit()
    print("\nDemo dossier seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
