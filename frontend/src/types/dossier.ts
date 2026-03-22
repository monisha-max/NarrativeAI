export interface DossierEvent {
  id: string;
  event_type: "corporate" | "regulatory" | "financial" | "management" | "market" | "legal";
  title: string;
  summary: string;
  occurred_at: string;
  entities_involved: string[] | null;
  sentiment_scores: SentimentScores | null;
  market_impact: number | null;
  fog_density: number;
}

export interface Dossier {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  status: string;
  velocity: string;
  article_count: number;
  tags: string[] | null;
  created_at: string;
  updated_at: string;
  events: DossierEvent[];
}

export interface DossierListResponse {
  dossiers: Dossier[];
  total: number;
}

export interface SentimentScores {
  market_confidence: number;
  regulatory_heat: number;
  media_tone: number;
  stakeholder_sentiment: number;
}
