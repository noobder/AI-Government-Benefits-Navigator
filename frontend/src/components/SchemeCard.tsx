import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { RecommendedScheme } from "../types/scheme";
import EligibilityBadge from "./EligibilityBadge";
import EligibilityBreakdown from "./EligibilityBreakdown";
import DocumentChecklist from "./DocumentChecklist";
import { Button, buttonClasses } from "./Button";

const CATEGORY_EMOJI: Record<string, string> = {
  Education: "🎓",
  Agriculture: "🌾",
  "Financial Assistance": "💰",
  Housing: "🏠",
  Employment: "💼",
  Women: "👩",
  Disability: "♿",
  "Senior Citizens": "👴",
  Healthcare: "🏥",
  Entrepreneurship: "🏪",
};

export default function SchemeCard({ item }: { item: RecommendedScheme }) {
  const [showWhy, setShowWhy] = useState(false);
  const [showDocs, setShowDocs] = useState(false);
  const emoji = CATEGORY_EMOJI[item.scheme.category] ?? "📋";
  const { t } = useTranslation();

  return (
    <article className="rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-sm">
      <div className="mb-2 flex items-start justify-between gap-3">
        <h3 className="text-lg font-bold text-[var(--ink)]">
          <span aria-hidden className="mr-1">
            {emoji}
          </span>
          {item.scheme.scheme_name}
        </h3>
        <EligibilityBadge status={item.eligibility.status} />
      </div>

      <p className="mb-3 text-sm text-[var(--ink-muted)]">{item.scheme.description}</p>

      <div className="mb-3 flex flex-wrap gap-2 text-xs text-[var(--ink-muted)]">
        <span className="rounded-full bg-[var(--surface-2)] px-2 py-1">
          {t(`common.category.${item.scheme.category}`, item.scheme.category)}
        </span>
        <span className="rounded-full bg-[var(--surface-2)] px-2 py-1">
          {t(`common.level.${item.scheme.level}`, item.scheme.level)}
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant={showWhy ? "primary" : "secondary"}
          onClick={() => setShowWhy((v) => !v)}
          aria-expanded={showWhy}
        >
          {showWhy ? t("scheme.hide") : t("scheme.whyOrMissing")}
        </Button>
        <Button
          type="button"
          variant={showDocs ? "primary" : "secondary"}
          onClick={() => setShowDocs((v) => !v)}
          aria-expanded={showDocs}
        >
          {showDocs ? t("scheme.hideDocuments") : t("scheme.documentsNeeded")}
        </Button>
        <Link to={`/schemes/${item.scheme.scheme_id}`} className={buttonClasses({ variant: "primary" })}>
          {t("scheme.viewDetails")}
        </Link>
      </div>

      {showWhy && (
        <div className="mt-4">
          <EligibilityBreakdown item={item} />
        </div>
      )}
      {showDocs && (
        <div className="mt-4 rounded-xl bg-[var(--surface-2)] p-4">
          <DocumentChecklist documents={item.documents} />
        </div>
      )}
    </article>
  );
}
