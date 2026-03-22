export interface GuidedPrompt {
  key: string;
  label: string;
}

export interface BriefingRequest {
  prompt_key?: string;
  custom_query?: string;
  user_type?: string;
  language?: string;
  perspective?: Record<string, number>;
}

export interface BriefingResponse {
  prompt_used: string;
  response_text: string;
  sources: Record<string, unknown>[];
  follow_up_prompts: string[];
}
