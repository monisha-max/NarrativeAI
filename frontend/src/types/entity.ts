export interface Entity {
  id: string;
  name: string;
  entity_type: "company" | "person" | "regulator" | "investor" | "sector";
  description: string | null;
  aliases: Record<string, string[]> | null;
}

export interface EntityRelationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: string;
  weight: number;
  details: Record<string, unknown> | null;
}

export interface EntityGraph {
  entities: Entity[];
  relationships: EntityRelationship[];
}
