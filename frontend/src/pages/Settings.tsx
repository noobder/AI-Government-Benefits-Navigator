import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAppState, type Theme } from "../hooks/useAppState";
import { Button } from "../components/Button";

export default function Settings() {
  const {
    language,
    setLanguage,
    largeText,
    setLargeText,
    highContrast,
    setHighContrast,
    theme,
    setTheme,
    simpleMode,
    setSimpleMode,
    signInputEnabled,
    setSignInputEnabled,
    signAnimationEnabled,
    setSignAnimationEnabled,
    userId,
  } = useAppState();
  const { t } = useTranslation();
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);

  const loadMetrics = async () => {
    const resp = await fetch("/api/metrics");
    setMetrics(await resp.json());
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="text-2xl font-bold text-[var(--ink)]">{t("settings.title")}</h1>

      <div className="mt-6 space-y-4 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-6">
        <Row label={t("settings.language")}>
          <select value={language} onChange={(e) => setLanguage(e.target.value)} className="input max-w-[10rem]">
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
            <option value="ta">தமிழ்</option>
          </select>
        </Row>
        <Row label={t("settings.theme")}>
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value as Theme)}
            className="input max-w-[10rem]"
          >
            <option value="system">{t("settings.themeSystem")}</option>
            <option value="light">{t("settings.themeLight")}</option>
            <option value="dark">{t("settings.themeDark")}</option>
          </select>
        </Row>
        <Row label={t("settings.largeText")}>
          <Toggle checked={largeText} onChange={setLargeText} label={t("settings.largeText")} />
        </Row>
        <Row label={t("settings.highContrast")}>
          <Toggle checked={highContrast} onChange={setHighContrast} label={t("settings.highContrast")} />
        </Row>
        <Row label={t("settings.profileId")}>
          <span className="font-mono text-xs text-[var(--ink-muted)]">{userId ?? t("settings.notCreatedYet")}</span>
        </Row>
      </div>

      <div className="mt-6 space-y-4 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-6">
        <div>
          <Row label={t("accessibility.simpleMode")}>
            <Toggle checked={simpleMode} onChange={setSimpleMode} label={t("accessibility.simpleMode")} />
          </Row>
          <p className="mt-1 text-xs text-[var(--ink-muted)]">{t("accessibility.simpleModeDesc")}</p>
        </div>
        <div>
          <Row label={t("accessibility.signAnimation")}>
            <Toggle
              checked={signAnimationEnabled}
              onChange={setSignAnimationEnabled}
              label={t("accessibility.signAnimation")}
            />
          </Row>
          <p className="mt-1 text-xs text-[var(--ink-muted)]">{t("accessibility.signAnimationDesc")}</p>
        </div>
        <div>
          <Row label={t("accessibility.signInput")}>
            <Toggle checked={signInputEnabled} onChange={setSignInputEnabled} label={t("accessibility.signInput")} />
          </Row>
          <p className="mt-1 text-xs text-[var(--ink-muted)]">{t("accessibility.signInputDesc")}</p>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-6">
        <h2 className="text-lg font-bold text-[var(--ink)]">{t("settings.platformMetrics")}</h2>
        <p className="text-sm text-[var(--ink-muted)]">{t("settings.metricsDesc")}</p>
        <Button variant="secondary" onClick={loadMetrics} className="mt-3">
          {t("settings.loadMetrics")}
        </Button>
        {metrics && (
          <pre className="mt-3 overflow-x-auto rounded-lg bg-[var(--surface-2)] p-3 text-xs text-[var(--ink)]">
            {JSON.stringify(metrics, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex min-h-[44px] items-center justify-between gap-3">
      <span className="text-sm font-semibold text-[var(--ink)]">{label}</span>
      {children}
    </div>
  );
}

function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      className={`h-8 w-14 flex-shrink-0 rounded-full p-1 transition ${
        checked ? "bg-brand-700" : "bg-[var(--surface-3)]"
      }`}
    >
      <span
        className={`block h-6 w-6 rounded-full bg-white shadow transition-transform ${checked ? "translate-x-6" : "translate-x-0"}`}
      />
    </button>
  );
}
