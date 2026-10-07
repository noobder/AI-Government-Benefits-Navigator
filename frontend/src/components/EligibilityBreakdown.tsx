import { useTranslation } from "react-i18next";
import type { RecommendedScheme } from "../types/scheme";

function fieldLabel(field: string) {
  return field.replace(/_/g, " ");
}

export default function EligibilityBreakdown({ item }: { item: RecommendedScheme }) {
  const { eligibility } = item;
  const { t } = useTranslation();
  return (
    <div className="space-y-3 rounded-xl bg-[var(--surface-2)] p-4">
      <div>
        <h4 className="mb-1 text-sm font-bold text-[var(--ink)]">{t("scheme.whyRecommended")}</h4>
        <ul className="space-y-1 text-sm">
          {eligibility.matched_conditions.map((c, i) => (
            <li key={i} className="flex items-start gap-2 text-[var(--brand)]">
              <span aria-hidden>✓</span>
              <span>{c.reason}</span>
            </li>
          ))}
          {eligibility.matched_conditions.length === 0 && (
            <li className="text-[var(--ink-muted)]">{t("scheme.noConfirmedMatches")}</li>
          )}
        </ul>
      </div>

      {eligibility.missing_conditions.length > 0 && (
        <div>
          <h4 className="mb-1 text-sm font-bold text-[var(--ink)]">{t("scheme.whatMissing")}</h4>
          <ul className="space-y-1 text-sm">
            {eligibility.missing_conditions.map((c, i) => (
              <li key={i} className="flex items-start gap-2 text-[var(--accent)]">
                <span aria-hidden>⚠</span>
                <span>{t("scheme.needField", { field: fieldLabel(c.field) })}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {eligibility.failed_conditions.length > 0 && (
        <div>
          <h4 className="mb-1 text-sm font-bold text-[var(--ink)]">{t("scheme.conditionsNotMet")}</h4>
          <ul className="space-y-1 text-sm">
            {eligibility.failed_conditions.map((c, i) => (
              <li key={i} className="flex items-start gap-2 text-[var(--danger)]">
                <span aria-hidden>✗</span>
                <span>{c.reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* c.reason / explanation come from the backend eligibility engine and
          are English-only today — see the Known limitations note. */}
      <p className="text-xs italic text-[var(--ink-muted)]">{eligibility.explanation}</p>
    </div>
  );
}
