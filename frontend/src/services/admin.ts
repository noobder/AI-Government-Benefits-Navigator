import { api } from "./api";
import type { Account } from "../types/auth";
import type { SchemeAdmin } from "../types/scheme";

export interface AuditLogEntry {
  id: string;
  admin_account_id: string;
  action: string;
  target_type: string;
  target_id: string;
  detail: Record<string, unknown>;
  created_at: string;
}

export const adminApi = {
  listSchemes: () => api.get<SchemeAdmin[]>("/admin/schemes"),
  createScheme: (payload: Record<string, unknown>) => api.post<SchemeAdmin>("/admin/schemes", payload),
  updateScheme: (schemeId: string, payload: Record<string, unknown>) =>
    api.put<SchemeAdmin>(`/admin/schemes/${schemeId}`, payload),
  deleteScheme: (schemeId: string) => api.delete<void>(`/admin/schemes/${schemeId}`),
  listAccounts: () => api.get<Account[]>("/admin/accounts"),
  auditLog: () => api.get<AuditLogEntry[]>("/admin/audit-log"),
};
