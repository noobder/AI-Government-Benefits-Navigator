import { useTranslation } from "react-i18next";

export default function ApplicationSteps({ steps }: { steps: string[] }) {
  const { t } = useTranslation();
  if (steps.length === 0) {
    return <p className="text-sm text-[var(--ink-muted)]">{t("scheme.noStepsOnRecord")}</p>;
  }
  return (
    <ol className="space-y-2">
      {steps.map((step, i) => (
        <li key={i} className="flex gap-3 text-sm">
          <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
            {i + 1}
          </span>
          <span className="pt-0.5">{step}</span>
        </li>
      ))}
    </ol>
  );
}
