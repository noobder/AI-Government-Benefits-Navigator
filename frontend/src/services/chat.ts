import { api } from "./api";
import type { ChatResponse } from "../types/eligibility";

export const chatApi = {
  send: (message: string, language: string, knownProfile: Record<string, unknown>, userId?: string) =>
    api.post<ChatResponse>("/chat", {
      message,
      language,
      known_profile: knownProfile,
      user_id: userId,
    }),
};
