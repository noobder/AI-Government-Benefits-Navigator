import { useTranslation } from "react-i18next";
import { useAppState } from "../hooks/useAppState";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी" },
  { code: "ta", label: "தமிழ்" },
];

export default function LanguageSelector() {
  const { language, setLanguage } = useAppState();
  const { t } = useTranslation();
  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="sr-only">{t("common.selectLanguage")}</span>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="min-h-[44px] rounded-xl border border-[var(--line-strong)] bg-[var(--surface)] px-3 py-2 text-sm font-medium text-[var(--ink)]"
        aria-label={t("common.selectLanguage")}
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>
            {l.label}
          </option>
        ))}
      </select>
    </label>
  );
}
