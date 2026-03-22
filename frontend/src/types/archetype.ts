export interface ArchetypePhase {
  phase_number: number;
  name: string;
  description: string;
  typical_duration_days: number | null;
  transition_indicators: string[] | null;
}

export interface Archetype {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string | null;
  avg_duration_months: number;
  reference_cases: string[] | null;
  phases: ArchetypePhase[];
}

export interface StoryDNA {
  archetype: Archetype;
  current_phase: number;
  confidence: number;
  phase_prediction: {
    next_phase: number;
    probability: number;
    estimated_days: number;
    trigger_events: string[];
  } | null;
  silence_alert: {
    days_silent: number;
    baseline_rate: number;
    expected_events: number;
    severity: string;
  } | null;
}
