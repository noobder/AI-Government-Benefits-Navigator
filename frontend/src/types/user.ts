export interface UserProfile {
  id?: string;
  age?: number | null;
  gender?: string | null;
  state?: string | null;
  district?: string | null;
  residence_type?: string | null;
  occupation?: string | null;
  annual_income?: number | null;
  education_level?: string | null;
  student?: boolean | null;
  course?: string | null;
  previous_academic_percentage?: number | null;
  family_size?: number | null;
  land_ownership?: string | null;
  land_area_acres?: number | null;
  employment_status?: string | null;
  disability_status?: boolean | null;
  extra_attributes?: Record<string, unknown>;
  language?: string;
}
