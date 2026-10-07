import { createContext, useContext } from "react";
import type { UserProfile } from "../types/user";
import type { Account } from "../types/auth";

export type Theme = "light" | "dark" | "system";

export interface AppState {
  userId: string | null;
  setUserId: (id: string | null) => void;
  account: Account | null;
  setAccount: (a: Account | null) => void;
  authLoading: boolean;
  language: string;
  setLanguage: (lang: string) => void;
  profile: UserProfile;
  setProfile: (p: UserProfile) => void;
  largeText: boolean;
  setLargeText: (v: boolean) => void;
  highContrast: boolean;
  setHighContrast: (v: boolean) => void;
  theme: Theme;
  setTheme: (t: Theme) => void;
  simpleMode: boolean;
  setSimpleMode: (v: boolean) => void;
  signInputEnabled: boolean;
  setSignInputEnabled: (v: boolean) => void;
  signAnimationEnabled: boolean;
  setSignAnimationEnabled: (v: boolean) => void;
}

export const AppContext = createContext<AppState | null>(null);

export function useAppState(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppState must be used within AppProvider");
  return ctx;
}
