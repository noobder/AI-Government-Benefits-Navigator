import { useTranslation } from "react-i18next";

export default function LoadingState({ label }: { label?: string }) {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-center gap-3 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-8" role="status" aria-live="polite">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" aria-hidden />
      <span className="text-sm font-medium text-[var(--ink-muted)]">{label ?? t("benefits.finding")}</span>
    </div>
  );
}
