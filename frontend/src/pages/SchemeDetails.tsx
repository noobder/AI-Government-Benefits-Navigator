import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LoadingState from "../components/LoadingState";
import EligibilityBadge from "../components/EligibilityBadge";
import EligibilityBreakdown from "../components/EligibilityBreakdown";
import DocumentChecklist from "../components/DocumentChecklist";
import ApplicationSteps from "../components/ApplicationSteps";
import SourceCard from "../components/SourceCard";
import { Button } from "../components/Button";
import { useAppState } from "../hooks/useAppState";
import { schemesApi } from "../services/schemes";
import type { RecommendedScheme, SchemeOut } from "../types/scheme";

export default function SchemeDetails() {
  const { schemeId } = useParams<{ schemeId: string }>();
  const { profile, userId, language } = useAppState();
  const { t } = useTranslation();
  const [scheme, setScheme] = useState<SchemeOut | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendedScheme | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!schemeId) return;
    let cancelled = false;
    async function load() {
      setIsLoading(true);
      const s = await schemesApi.get(schemeId!, language);
      if (cancelled) return;
      setScheme(s);
      try {
        const matches = await schemesApi.match(profile as Record<string, unknown>, "", language);
        const found = matches.find((m) => m.scheme.scheme_id === schemeId);
        if (!cancelled) setRecommendation(found ?? null);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [schemeId, profile, language]);

  const handleSave = async () => {
    if (!userId || !schemeId) {
      setSavedMessage(t("schemeDetails.saveNoProfile"));
      return;
    }
    await schemesApi.save(schemeId, userId);
    setSavedMessage(t("schemeDetails.savedMessage"));
  };

  if (isLoading || !scheme) return <div className="mx-auto max-w-4xl px-4 py-8"><LoadingState /></div>;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link to="/benefits" className="text-sm font-semibold text-brand-700">
        {t("schemeDetails.back")}
      </Link>

      <div className="mt-3 flex flex-wrap items-start justify-between gap-3">
        <h1 className="text-2xl font-bold text-[var(--ink)]">{scheme.scheme_name}</h1>
        {recommendation && <EligibilityBadge status={recommendation.eligibility.status} />}
      </div>

      <p className="mt-2 text-[var(--ink-muted)]">{scheme.description}</p>

      <div className="mt-4 flex flex-wrap gap-2">
        <Button onClick={handleSave} className="!border-transparent !bg-[var(--accent)] hover:!brightness-95">
          {t("schemeDetails.save")}
        </Button>
      </div>
      {savedMessage && <p className="mt-2 text-sm text-brand-700">{savedMessage}</p>}

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="space-y-6 md:col-span-2">
          {recommendation && (
            <Section title={t("scheme.whyOrMissing")}>
              <EligibilityBreakdown item={recommendation} />
            </Section>
          )}

          <Section title={t("scheme.benefits")}>
            <ul className="list-inside list-disc space-y-1 text-sm text-[var(--ink)]">
              {scheme.benefits.map((b, i) => (
                <li key={i}>{b}</li>
              ))}
            </ul>
          </Section>

          <Section title={t("scheme.requiredDocuments")}>
            <DocumentChecklist
              documents={
                recommendation?.documents ??
                scheme.required_documents.map((name) => ({ name, status: "possibly_required" as const }))
              }
            />
          </Section>

          <Section title={t("scheme.howToApply")}>
            <ApplicationSteps steps={scheme.application_steps} />
          </Section>
        </div>

        <div className="space-y-4">
          <SourceCard scheme={scheme} />
          <div className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-4 text-sm">
            <p className="font-bold text-[var(--ink)]">{t("scheme.ministryDepartment")}</p>
            <p className="text-[var(--ink-muted)]">{scheme.ministry ?? "—"}</p>
            <p className="text-[var(--ink-muted)]">{scheme.department ?? "—"}</p>
            <p className="mt-2 font-bold text-[var(--ink)]">{t("scheme.applicableStates")}</p>
            <p className="text-[var(--ink-muted)]">
              {scheme.applicable_states.join(", ") || t("scheme.allStates")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="mb-2 text-lg font-bold text-[var(--ink)]">{title}</h2>
      {children}
    </section>
  );
}
