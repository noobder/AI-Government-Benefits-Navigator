import type { RecommendedScheme } from "./scheme";

export interface ChatResponse {
  reply_text: string;
  language: string;
  extracted_profile: Record<string, unknown>;
  missing_fields: string[];
  follow_up_question: string | null;
  recommendations: RecommendedScheme[];
}

export interface DashboardData {
  likely_eligible_count: number;
  needs_verification_count: number;
  saved_count: number;
  likely_eligible_scheme_ids: string[];
  needs_verification_scheme_ids: string[];
  saved_scheme_ids: string[];
  recommended_actions: string[];
}
