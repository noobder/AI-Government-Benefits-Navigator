import { api } from "./api";
import type { Account } from "../types/auth";

export const authApi = {
  register: (email: string, password: string) => api.post<Account>("/auth/register", { email, password }),
  login: (email: string, password: string) => api.post<Account>("/auth/login", { email, password }),
  logout: () => api.post<{ logged_out: boolean }>("/auth/logout"),
  me: () => api.get<Account | null>("/auth/me"),
};
