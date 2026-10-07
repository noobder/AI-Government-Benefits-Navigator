import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAppState } from "../hooks/useAppState";
import { adminApi, type AuditLogEntry } from "../services/admin";
import type { SchemeAdmin } from "../types/scheme";
import type { Account } from "../types/auth";
import { Button, buttonClasses } from "../components/Button";
import AdminSchemeForm from "../components/AdminSchemeForm";
import LoadingState from "../components/LoadingState";

type Tab = "schemes" | "accounts" | "audit";

export default function Admin() {
  const { account, authLoading } = useAppState();
  const { t } = useTranslation();
  const [tab, setTab] = useState<Tab>("schemes");

  if (authLoading) return <div className="mx-auto max-w-5xl px-4 py-8"><LoadingState /></div>;
  if (!account) return <Navigate to="/login" state={{ from: "/admin" }} replace />;
  if (account.role !== "admin") {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center">
        <p className="text-lg font-bold text-[var(--ink)]">{t("admin.notAuthorized")}</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-2xl font-bold text-[var(--ink)]">{t("admin.title")}</h1>

      <div className="mt-4 flex gap-2 border-b border-[var(--line)]">
        {(["schemes", "accounts", "audit"] as Tab[]).map((tabKey) => (
          <button
            key={tabKey}
            onClick={() => setTab(tabKey)}
            className={`min-h-[44px] border-b-2 px-3 text-sm font-semibold ${
              tab === tabKey ? "border-brand-700 text-brand-700" : "border-transparent text-[var(--ink-muted)]"
            }`}
          >
            {t(`admin.tab.${tabKey}`)}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === "schemes" && <SchemesTab />}
        {tab === "accounts" && <AccountsTab />}
        {tab === "audit" && <AuditTab />}
      </div>
    </div>
  );
}

function SchemesTab() {
  const { t } = useTranslation();
  const [schemes, setSchemes] = useState<SchemeAdmin[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<SchemeAdmin | null | "new">(null);

  const load = async () => {
    setIsLoading(true);
    setError(null);
    try {
      setSchemes(await adminApi.listSchemes());
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.genericError"));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDelete = async (schemeId: string) => {
    if (!window.confirm(t("admin.confirmDelete"))) return;
    try {
      await adminApi.deleteScheme(schemeId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.genericError"));
    }
  };

  if (editing) {
    return (
      <AdminSchemeForm
        scheme={editing === "new" ? undefined : editing}
        onCancel={() => setEditing(null)}
        onSubmit={async (payload) => {
          if (editing === "new") {
            await adminApi.createScheme(payload);
          } else {
            await adminApi.updateScheme(editing.scheme_id, payload);
          }
          setEditing(null);
          await load();
        }}
      />
    );
  }

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <Button onClick={() => setEditing("new")}>{t("admin.newScheme")}</Button>
      </div>

      {isLoading && <LoadingState />}
      {error && <p className="rounded-xl bg-[var(--danger-weak)] p-3 text-sm text-[var(--danger)]">{error}</p>}

      {!isLoading && !error && (
        <div className="overflow-x-auto rounded-xl border border-[var(--line)] bg-[var(--surface)]">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--line)] bg-[var(--surface-2)]">
                <th className="p-3">{t("admin.schemeId")}</th>
                <th className="p-3">{t("admin.schemeName")}</th>
                <th className="p-3">{t("benefits.category")}</th>
                <th className="p-3">{t("admin.level")}</th>
                <th className="p-3" />
              </tr>
            </thead>
            <tbody>
              {schemes.map((s) => (
                <tr key={s.scheme_id} className="border-b border-[var(--line)] align-top">
                  <td className="p-3 font-mono text-xs text-[var(--ink-muted)]">{s.scheme_id}</td>
                  <td className="p-3 text-[var(--ink)]">{s.scheme_name}</td>
                  <td className="p-3 text-[var(--ink-muted)]">{s.category}</td>
                  <td className="p-3 text-[var(--ink-muted)]">{s.level}</td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      <button onClick={() => setEditing(s)} className={buttonClasses({ variant: "secondary" })}>
                        {t("admin.edit")}
                      </button>
                      <button
                        onClick={() => handleDelete(s.scheme_id)}
                        className={buttonClasses({ variant: "danger" })}
                      >
                        {t("admin.delete")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function AccountsTab() {
  const { t } = useTranslation();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    adminApi
      .listAccounts()
      .then(setAccounts)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <LoadingState />;

  return (
    <div className="overflow-x-auto rounded-xl border border-[var(--line)] bg-[var(--surface)]">
      <table className="w-full min-w-[500px] text-left text-sm">
        <thead>
          <tr className="border-b border-[var(--line)] bg-[var(--surface-2)]">
            <th className="p-3">{t("auth.email")}</th>
            <th className="p-3">{t("admin.role")}</th>
            <th className="p-3">{t("admin.createdAt")}</th>
            <th className="p-3">{t("admin.lastLogin")}</th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((a) => (
            <tr key={a.id} className="border-b border-[var(--line)]">
              <td className="p-3 text-[var(--ink)]">{a.email}</td>
              <td className="p-3 text-[var(--ink-muted)]">{a.role}</td>
              <td className="p-3 text-[var(--ink-muted)]">{new Date(a.created_at).toLocaleDateString()}</td>
              <td className="p-3 text-[var(--ink-muted)]">
                {a.last_login_at ? new Date(a.last_login_at).toLocaleString() : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AuditTab() {
  const { t } = useTranslation();
  const [rows, setRows] = useState<AuditLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    adminApi
      .auditLog()
      .then(setRows)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <LoadingState />;
  if (rows.length === 0) return <p className="text-sm text-[var(--ink-muted)]">{t("admin.noAuditEntries")}</p>;

  return (
    <ul className="space-y-2">
      {rows.map((r) => (
        <li key={r.id} className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-3 text-sm">
          <span className="font-mono text-xs text-[var(--ink-muted)]">{new Date(r.created_at).toLocaleString()}</span>
          <span className="ml-2 font-semibold text-[var(--ink)]">{r.action}</span>
          <span className="ml-2 text-[var(--ink-muted)]">
            {r.target_type}:{r.target_id}
          </span>
        </li>
      ))}
    </ul>
  );
}
