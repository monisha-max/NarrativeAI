export interface RippleConnection {
  source_dossier_id: string;
  target_dossier_id: string;
  connection_type: string;
  strength: number;
  shared_entities: Record<string, unknown> | null;
  description: string | null;
}

export interface RippleAlert {
  id: string;
  source_dossier_id: string;
  target_dossier_id: string;
  impact_description: string;
  magnitude: number;
  status: string;
  created_at: string;
}
