import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.session import async_session
from app.models.article import Article
from app.models.entity import Entity, EntityRelationship
from app.services.nlp import extract_entities
from app.services.claude import claude_service


class EntityAgent(BaseAgent):
    """Extracts entities, resolves coreferences, and builds relationship graphs."""

    name = "entity"

    async def execute(self, context: AgentContext) -> AgentResult:
        dossier_id = context.dossier_id
        self.logger.info("entity.start", dossier_id=dossier_id)

        # Get new articles from ingestion results
        ingestion_data = context.parent_results.get("ingestion")
        article_ids = []
        if ingestion_data and ingestion_data.success:
            article_ids = [a["id"] for a in ingestion_data.data.get("articles", [])]

        async with async_session() as db:
            # Load articles
            if article_ids:
                result = await db.execute(
                    select(Article).where(Article.id.in_([uuid.UUID(aid) for aid in article_ids]))
                )
                articles = result.scalars().all()
            elif dossier_id:
                result = await db.execute(
                    select(Article).where(Article.dossier_id == uuid.UUID(dossier_id))
                )
                articles = result.scalars().all()
            else:
                return AgentResult(
                    agent_name=self.name, success=True,
                    data={"entities_extracted": 0, "relationships_found": 0},
                )

            if not articles:
                return AgentResult(
                    agent_name=self.name, success=True,
                    data={"entities_extracted": 0, "relationships_found": 0},
                )

            self.logger.info("entity.processing", article_count=len(articles))

            # Phase 1: Extract entities from each article using spaCy
            all_raw_entities = []
            entity_cooccurrences = defaultdict(lambda: defaultdict(int))

            for article in articles:
                text = f"{article.title}\n\n{article.content}"
                raw_entities = extract_entities(text)

                # Track entities per article for co-occurrence
                article_entity_names = set()
                for ent in raw_entities:
                    all_raw_entities.append({
                        "text": ent["text"],
                        "label": ent["label"],
                        "article_id": str(article.id),
                    })
                    article_entity_names.add(ent["text"])

                # Build co-occurrence matrix (entities appearing in same article)
                names = list(article_entity_names)
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        entity_cooccurrences[names[i]][names[j]] += 1
                        entity_cooccurrences[names[j]][names[i]] += 1

            # Phase 2: Classify and deduplicate entities using LLM
            unique_entities = {}
            for ent in all_raw_entities:
                name = ent["text"]
                if name not in unique_entities:
                    unique_entities[name] = {
                        "name": name,
                        "spacy_label": ent["label"],
                        "mention_count": 0,
                        "article_ids": set(),
                    }
                unique_entities[name]["mention_count"] += 1
                unique_entities[name]["article_ids"].add(ent["article_id"])

            # Filter to entities with 2+ mentions or that are organizations/people
            significant_entities = {
                k: v for k, v in unique_entities.items()
                if v["mention_count"] >= 2 or v["spacy_label"] in ("ORG", "PERSON")
            }

            # Phase 3: Use Claude to classify entity types and extract relationships
            entity_names = list(significant_entities.keys())[:50]  # Limit for API cost
            if entity_names:
                classification = await self._classify_entities(entity_names, context.query or "")
            else:
                classification = {"entities": [], "relationships": []}

            # Phase 4: Store entities in database
            entity_map = {}  # name -> Entity model
            for ent_data in classification.get("entities", []):
                name = ent_data.get("name", "")
                if not name:
                    continue

                # Check if entity already exists
                existing = await db.execute(
                    select(Entity).where(Entity.name == name)
                )
                entity = existing.scalar_one_or_none()

                if not entity:
                    entity = Entity(
                        name=name,
                        entity_type=ent_data.get("type", "company"),
                        description=ent_data.get("description"),
                        aliases={"aliases": ent_data.get("aliases", [])},
                    )
                    db.add(entity)
                    await db.flush()

                entity_map[name] = entity

            # Phase 5: Create relationships
            relationships_created = 0
            for rel_data in classification.get("relationships", []):
                source_name = rel_data.get("source")
                target_name = rel_data.get("target")

                if source_name in entity_map and target_name in entity_map:
                    source_entity = entity_map[source_name]
                    target_entity = entity_map[target_name]

                    # Check if relationship already exists
                    existing_rel = await db.execute(
                        select(EntityRelationship).where(
                            EntityRelationship.source_entity_id == source_entity.id,
                            EntityRelationship.target_entity_id == target_entity.id,
                            EntityRelationship.dossier_id == uuid.UUID(dossier_id) if dossier_id else True,
                        )
                    )
                    if not existing_rel.scalar_one_or_none():
                        # Use co-occurrence as weight
                        weight = entity_cooccurrences.get(source_name, {}).get(target_name, 1)
                        weight = min(weight / 10.0, 1.0)  # Normalize

                        rel = EntityRelationship(
                            source_entity_id=source_entity.id,
                            target_entity_id=target_entity.id,
                            relationship_type=rel_data.get("type", "related"),
                            weight=weight,
                            details={"description": rel_data.get("description", "")},
                            dossier_id=uuid.UUID(dossier_id) if dossier_id else None,
                        )
                        db.add(rel)
                        relationships_created += 1

            await db.commit()

        self.logger.info(
            "entity.complete",
            raw_entities=len(all_raw_entities),
            unique_entities=len(significant_entities),
            stored_entities=len(entity_map),
            relationships=relationships_created,
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "entities_extracted": len(entity_map),
                "relationships_found": relationships_created,
                "entities": [
                    {"name": e.name, "type": e.entity_type, "id": str(e.id)}
                    for e in entity_map.values()
                ],
            },
        )

    async def _classify_entities(self, entity_names: list[str], story_context: str) -> dict:
        """Use Claude to classify entities and extract relationships."""
        prompt = f"""Analyze these entities from a business news story about "{story_context}".

Entity names found: {', '.join(entity_names)}

For each significant entity, provide:
1. name: exact name
2. type: one of [company, person, regulator, investor, sector, legal_body]
3. description: one sentence about their role in this story
4. aliases: list of alternative names/abbreviations

Also identify relationships between entities:
1. source: entity name
2. target: entity name
3. type: one of [ownership, regulatory, legal, financial, employment, partnership, competitor, subsidiary, investor]
4. description: brief description of the relationship

Return JSON with keys "entities" and "relationships"."""

        try:
            result = await claude_service.complete_json(
                system_prompt="You are an expert at extracting business entities and relationships from Indian news. Return valid JSON only.",
                messages=[{"role": "user", "content": prompt}],
            )
            return result
        except Exception as e:
            self.logger.warning("entity.classify.error", error=str(e))
            # Fallback: create basic entities without LLM classification
            return {
                "entities": [
                    {"name": name, "type": "company", "description": "", "aliases": []}
                    for name in entity_names[:20]
                ],
                "relationships": [],
            }
