import { useTranslation } from "react-i18next";
import type { EligibilityStatus } from "../types/scheme";

const CONFIG: Record<EligibilityStatus, { emoji: string; classes: string }> = {
  likely_eligible: { emoji: "🟢", classes: "bg-green-100 text-green-800" },
  possibly_eligible: { emoji: "🟡", classes: "bg-amber-100 text-amber-800" },
  missing_information: { emoji: "🟡", classes: "bg-amber-100 text-amber-800" },
  not_matching: { emoji: "🔴", classes: "bg-red-100 text-red-800" },
  unable_to_determine: { emoji: "⚪", classes: "bg-neutral-100 text-neutral-700" },
};

export default function EligibilityBadge({ status }: { status: EligibilityStatus }) {
  const { t } = useTranslation();
  const cfg = CONFIG[status] ?? CONFIG.unable_to_determine;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold ${cfg.classes}`}>
      <span aria-hidden>{cfg.emoji}</span>
      {t(`eligibility.${status}`, t("eligibility.unable_to_determine"))}
    </span>
  );
}
