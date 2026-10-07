import { useTranslation } from "react-i18next";
import type { SchemeOut } from "../types/scheme";

export default function SourceCard({ scheme }: { scheme: SchemeOut }) {
  const { t } = useTranslation();
  return (
    <div className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-4 text-sm">
      <p className="font-bold text-[var(--ink)]">{t("scheme.source")}</p>
      <p className="text-[var(--ink-muted)]">{scheme.source_name}</p>
      <p className="mt-2 font-bold text-[var(--ink)]">{t("scheme.lastVerified")}</p>
      <p className="text-[var(--ink-muted)]">{scheme.last_verified}</p>
      {scheme.is_demo && (
        <p className="mt-3 rounded-lg bg-[var(--accent-weak)] p-2 text-xs text-[var(--accent)]">
          {t("scheme.demoDisclaimer")}
        </p>
      )}
      <a
        href={scheme.official_url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-3 inline-flex min-h-[44px] items-center font-semibold text-brand-700 underline"
      >
        {t("scheme.openOfficialSource")}
      </a>
    </div>
  );
}
