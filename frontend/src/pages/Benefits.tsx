import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import SchemeCard from "../components/SchemeCard";
import EmptyState from "../components/EmptyState";
import LoadingState from "../components/LoadingState";
import { buttonClasses } from "../components/Button";
import { useAppState } from "../hooks/useAppState";
import { schemesApi } from "../services/schemes";
import { profileApi } from "../services/profile";
import type { RecommendedScheme } from "../types/scheme";
import type { DashboardData } from "../types/eligibility";

export default function Benefits() {
  const { profile, userId, language } = useAppState();
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const category = searchParams.get("category") ?? "";

  const [recommendations, setRecommendations] = useState<RecommendedScheme[]>([]);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);

  const hasProfile = useMemo(() => Object.values(profile).some((v) => v !== null && v !== undefined && v !== ""), [profile]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const results = await schemesApi.match(profile as Record<string, unknown>, category, language);
        if (!cancelled) setRecommendations(results);
        if (userId) {
          const dash = await profileApi.dashboard(userId, language);
          if (!cancelled) setDashboard(dash);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : t("benefits.loadError"));
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [profile, userId, category, language]); // eslint-disable-line react-hooks/exhaustive-deps

  const filtered = category
    ? recommendations.filter((r) => r.scheme.category === category)
    : recommendations;

  const toggleCompare = (id: string) => {
    setCompareIds((ids) => (ids.includes(id) ? ids.filter((x) => x !== id) : ids.length < 3 ? [...ids, id] : ids));
  };

  const compareItems = filtered.filter((r) => compareIds.includes(r.scheme.scheme_id));

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-[var(--ink)]">
          {t("benefits.title")}
          {category ? ` — ${t(`common.category.${category}`, category)}` : ""}
        </h1>
        <Link to="/profile" className={buttonClasses({ variant: "secondary" })}>
          {t("benefits.updateProfile")}
        </Link>
      </div>

      {dashboard && (
        <div className="mt-4 grid grid-cols-3 gap-3">
          <StatTile emoji="🟢" label={t("benefits.likelyEligible")} value={dashboard.likely_eligible_count} />
          <StatTile emoji="🟡" label={t("benefits.needsVerification")} value={dashboard.needs_verification_count} />
          <StatTile emoji="⭐" label={t("benefits.saved")} value={dashboard.saved_count} />
        </div>
      )}

      {dashboard && dashboard.recommended_actions.length > 0 && (
        <div className="mt-4 rounded-xl border border-brand-200 bg-brand-50 p-4">
          <h2 className="text-sm font-bold text-brand-800">{t("benefits.recommendedNextSteps")}</h2>
          <ul className="mt-1 list-inside list-disc text-sm text-brand-800">
            {dashboard.recommended_actions.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      )}

      {!hasProfile && (
        <div className="mt-6">
          <EmptyState
            title={t("benefits.incompleteTitle")}
            description={t("benefits.incompleteDesc")}
            action={
              <Link to="/profile" className={buttonClasses()}>
                {t("benefits.buildMyProfile")}
              </Link>
            }
          />
        </div>
      )}

      <div className="mt-6 space-y-4">
        {isLoading && <LoadingState label={t("benefits.finding")} />}
        {error && <p className="rounded-xl bg-[var(--danger-weak)] p-3 text-sm text-[var(--danger)]">{error}</p>}
        {!isLoading && !error && filtered.length === 0 && (
          <EmptyState
            title={t("benefits.noMatchTitle")}
            description={t("benefits.noMatchDesc")}
            action={
              <Link to="/chat" className={buttonClasses()}>
                {t("benefits.askAiInstead")}
              </Link>
            }
          />
        )}

        {filtered.map((r) => (
          <div key={r.scheme.scheme_id} className="relative">
            <label className="absolute right-5 top-5 z-10 flex items-center gap-1 rounded-full bg-[var(--surface)]/90 px-2 py-1 text-xs font-semibold shadow">
              <input
                type="checkbox"
                checked={compareIds.includes(r.scheme.scheme_id)}
                onChange={() => toggleCompare(r.scheme.scheme_id)}
              />
              {t("benefits.compare")}
            </label>
            <SchemeCard item={r} />
          </div>
        ))}
      </div>

      {compareItems.length >= 2 && (
        <div className="mt-8">
          <h2 className="mb-3 text-lg font-bold text-[var(--ink)]">{t("benefits.compareSchemes")}</h2>
          <div className="overflow-x-auto rounded-xl border border-[var(--line)] bg-[var(--surface)]">
            <table className="w-full min-w-[500px] text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--line)] bg-[var(--surface-2)]">
                  <th className="p-3">{t("benefits.feature")}</th>
                  {compareItems.map((r) => (
                    <th key={r.scheme.scheme_id} className="p-3">
                      {r.scheme.scheme_name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <CompareRow
                  label={t("benefits.category")}
                  items={compareItems}
                  render={(r) => t(`common.category.${r.scheme.category}`, r.scheme.category)}
                />
                <CompareRow
                  label={t("benefits.eligibility")}
                  items={compareItems}
                  render={(r) => t(`eligibility.${r.eligibility.status}`, r.eligibility.status.replace(/_/g, " "))}
                />
                <CompareRow label={t("scheme.benefits")} items={compareItems} render={(r) => r.scheme.benefits.join("; ")} />
                <CompareRow
                  label={t("benefits.documents")}
                  items={compareItems}
                  render={(r) => r.scheme.required_documents.join("; ")}
                />
                <CompareRow label={t("benefits.source")} items={compareItems} render={(r) => r.scheme.source_name} />
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function StatTile({ emoji, label, value }: { emoji: string; label: string; value: number }) {
  return (
    <div className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-4 text-center">
      <p className="text-2xl" aria-hidden>
        {emoji}
      </p>
      <p className="text-2xl font-extrabold text-[var(--ink)]">{value}</p>
      <p className="text-xs font-semibold text-[var(--ink-muted)]">{label}</p>
    </div>
  );
}

function CompareRow({
  label,
  items,
  render,
}: {
  label: string;
  items: RecommendedScheme[];
  render: (r: RecommendedScheme) => string;
}) {
  return (
    <tr className="border-b border-[var(--line)] align-top">
      <td className="p-3 font-semibold text-[var(--ink)]">{label}</td>
      {items.map((r) => (
        <td key={r.scheme.scheme_id} className="p-3 text-[var(--ink-muted)]">
          {render(r)}
        </td>
      ))}
    </tr>
  );
}
