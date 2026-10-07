import { api } from "./api";
import type { UserProfile } from "../types/user";
import type { DashboardData } from "../types/eligibility";

export const profileApi = {
  create: (profile: UserProfile) => api.post<UserProfile>("/profile", profile),
  get: (userId: string) => api.get<UserProfile>(`/profile/${userId}`),
  patch: (userId: string, fields: Record<string, unknown>) =>
    api.patch<UserProfile>(`/profile/${userId}`, { fields }),
  dashboard: (userId: string, language = "en") => api.get<DashboardData>(`/dashboard/${userId}?language=${language}`),
  extract: (text: string) => api.post<Partial<UserProfile>>("/profile/extract", { text }),
};
