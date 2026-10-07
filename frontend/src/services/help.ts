import { api } from "./api";

export interface HelpAnswer {
  answer: string;
  matched: boolean;
  topic: string | null;
}

export interface TutorialStep {
  step_id: string;
  route: string;
  title: string;
  narration: string;
}

export const helpApi = {
  ask: (question: string, language: string) => api.post<HelpAnswer>("/help/ask", { question, language }),
  tutorial: (language: string) => api.get<TutorialStep[]>(`/help/tutorial?language=${language}`),
};
