export interface SchemeOut {
  scheme_id: string;
  scheme_name: string;
  description: string;
  category: string;
  ministry?: string | null;
  department?: string | null;
  level: string;
  applicable_states: string[];
  target_beneficiaries: string[];
  benefits: string[];
  required_documents: string[];
  application_steps: string[];
  official_url: string;
  source_url: string;
  source_name: string;
  last_verified: string;
  languages: string[];
  is_demo: boolean;
}

export interface SchemeAdmin extends SchemeOut {
  eligibility_rules: Record<string, unknown>;
  exclusions: string[];
  translations?: Record<string, Record<string, unknown>>;
}

// What the admin create/edit form works with — a raw JSON string for
// eligibility_rules (edited as text) rather than forcing a full rule-tree
// UI builder for this pass.
export interface SchemeFormValues {
  scheme_id: string;
  scheme_name: string;
  description: string;
  category: string;
  ministry: string;
  department: string;
  level: string;
  applicable_states: string; // comma-separated in the form
  benefits: string; // one per line
  required_documents: string; // one per line
  application_steps: string; // one per line
  official_url: string;
  source_url: string;
  source_name: string;
  last_verified: string;
  is_demo: boolean;
  eligibility_rules_json: string;
}

export type EligibilityStatus =
  | "likely_eligible"
  | "possibly_eligible"
  | "missing_information"
  | "not_matching"
  | "unable_to_determine";

export interface ConditionResult {
  field: string;
  operator: string;
  expected_value: unknown;
  actual_value: unknown;
  result: boolean | null;
  reason: string;
}

export interface EligibilityResult {
  scheme_id: string;
  status: EligibilityStatus;
  matched_conditions: ConditionResult[];
  failed_conditions: ConditionResult[];
  missing_conditions: ConditionResult[];
  explanation: string;
}

export interface DocumentItem {
  name: string;
  status: "required" | "possibly_required";
}

export interface RecommendedScheme {
  scheme: SchemeOut;
  eligibility: EligibilityResult;
  why_recommended: string[];
  missing_information: string[];
  documents: DocumentItem[];
}
