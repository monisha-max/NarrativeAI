"""Seed the archetype library from JSON files."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from app.db.session import async_session, engine
from app.models.archetype import Archetype, ArchetypePhase
from app.models.base import Base


DATA_DIR = Path(__file__).parent.parent / "data" / "archetypes"


async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        for json_file in sorted(DATA_DIR.glob("*.json")):
            data = json.loads(json_file.read_text())

            # Check if already exists
            existing = await session.execute(
                select(Archetype).where(Archetype.slug == data["slug"])
            )
            if existing.scalar_one_or_none():
                print(f"  Skipping {data['name']} (already exists)")
                continue

            archetype = Archetype(
                name=data["name"],
                slug=data["slug"],
                description=data["description"],
                icon=data.get("icon"),
                avg_duration_months=data["avg_duration_months"],
                reference_cases=data.get("reference_cases"),
            )
            session.add(archetype)
            await session.flush()

            for phase_data in data["phases"]:
                phase = ArchetypePhase(
                    archetype_id=archetype.id,
                    phase_number=phase_data["phase_number"],
                    name=phase_data["name"],
                    description=phase_data["description"],
                    typical_duration_days=phase_data.get("typical_duration_days"),
                    transition_indicators=phase_data.get("transition_indicators"),
                )
                session.add(phase)

            print(f"  Seeded: {data['name']} ({len(data['phases'])} phases)")

        await session.commit()
    print("\nArchetype seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
