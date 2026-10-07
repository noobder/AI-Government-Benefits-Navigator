import { api } from "./api";
import type { RecommendedScheme, SchemeOut } from "../types/scheme";

export const schemesApi = {
  list: (params?: { category?: string; state?: string; language?: string }) => {
    const q = new URLSearchParams();
    if (params?.category) q.set("category", params.category);
    if (params?.state) q.set("state", params.state);
    if (params?.language) q.set("language", params.language);
    const qs = q.toString();
    return api.get<SchemeOut[]>(`/schemes${qs ? `?${qs}` : ""}`);
  },
  get: (schemeId: string, language = "en") => api.get<SchemeOut>(`/schemes/${schemeId}?language=${language}`),
  match: (profile: Record<string, unknown>, queryText = "", language = "en") =>
    api.post<RecommendedScheme[]>("/schemes/match", { profile, query_text: queryText, language }),
  save: (schemeId: string, userId: string) =>
    api.post<{ saved: boolean; id: string }>(`/schemes/${schemeId}/save`, { user_id: userId }),
};
