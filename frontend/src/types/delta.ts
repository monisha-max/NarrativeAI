export interface DeltaCard {
  dossier_slug: string;
  dossier_title: string;
  new_events_count: number;
  change_summary: string;
  sentiment_shift: Record<string, number> | null;
  new_entities: string[];
  predictions_tested: string[];
  phase_change: boolean;
  velocity_change: string | null;
  ripple_alerts: string[];
  significance_score: number;
  last_checked: string | null;
}

export interface DeltaResponse {
  cards: DeltaCard[];
  sixty_second_summary: {
    most_important_change: string;
    biggest_risk: string;
    actionable_insight: string;
  } | null;
}
