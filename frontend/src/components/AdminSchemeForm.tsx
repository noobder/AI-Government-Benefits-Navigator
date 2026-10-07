import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { SchemeAdmin } from "../types/scheme";
import { Button } from "./Button";

function toFormValues(scheme?: SchemeAdmin) {
  return {
    scheme_id: scheme?.scheme_id ?? "",
    scheme_name: scheme?.scheme_name ?? "",
    description: scheme?.description ?? "",
    category: scheme?.category ?? "Education",
    ministry: scheme?.ministry ?? "",
    department: scheme?.department ?? "",
    level: scheme?.level ?? "State",
    applicable_states: (scheme?.applicable_states ?? []).join(", "),
    benefits: (scheme?.benefits ?? []).join("\n"),
    required_documents: (scheme?.required_documents ?? []).join("\n"),
    application_steps: (scheme?.application_steps ?? []).join("\n"),
    official_url: scheme?.official_url ?? "",
    source_url: scheme?.source_url ?? "",
    source_name: scheme?.source_name ?? "",
    last_verified: scheme?.last_verified ?? new Date().toISOString().slice(0, 10),
    is_demo: scheme?.is_demo ?? true,
    eligibility_rules_json: JSON.stringify(
      scheme?.eligibility_rules ?? { operator: "AND", conditions: [] },
      null,
      2
    ),
    translations_json: JSON.stringify(scheme?.translations ?? {}, null, 2),
  };
}

const CATEGORIES = [
  "Education", "Agriculture", "Financial Assistance", "Housing", "Employment",
  "Women", "Disability", "Senior Citizens", "Healthcare", "Business", "Entrepreneurship",
];

export default function AdminSchemeForm({
  scheme,
  onSubmit,
  onCancel,
}: {
  scheme?: SchemeAdmin;
  onSubmit: (payload: Record<string, unknown>) => Promise<void>;
  onCancel: () => void;
}) {
  const { t } = useTranslation();
  const isEdit = Boolean(scheme);
  const [values, setValues] = useState(toFormValues(scheme));
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const set = <K extends keyof typeof values>(key: K, value: (typeof values)[K]) =>
    setValues((v) => ({ ...v, [key]: value }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setJsonError(null);

    let eligibilityRules: unknown;
    let translations: unknown;
    try {
      eligibilityRules = JSON.parse(values.eligibility_rules_json);
    } catch {
      setJsonError(t("admin.invalidJson"));
      return;
    }
    try {
      translations = JSON.parse(values.translations_json);
    } catch {
      setJsonError(t("admin.invalidJson"));
      return;
    }

    const payload: Record<string, unknown> = {
      scheme_name: values.scheme_name,
      description: values.description,
      category: values.category,
      ministry: values.ministry || null,
      department: values.department || null,
      level: values.level,
      applicable_states: values.applicable_states
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      benefits: values.benefits.split("\n").map((s) => s.trim()).filter(Boolean),
      required_documents: values.required_documents.split("\n").map((s) => s.trim()).filter(Boolean),
      application_steps: values.application_steps.split("\n").map((s) => s.trim()).filter(Boolean),
      official_url: values.official_url,
      source_url: values.source_url,
      source_name: values.source_name,
      last_verified: values.last_verified,
      is_demo: values.is_demo,
      eligibility_rules: eligibilityRules,
      translations,
    };
    if (!isEdit) payload.scheme_id = values.scheme_id;

    setIsSubmitting(true);
    try {
      await onSubmit(payload);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : t("common.genericError"));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-5">
      <h3 className="text-base font-bold text-[var(--ink)]">
        {isEdit ? t("admin.editScheme") : t("admin.newScheme")}
      </h3>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label={t("admin.schemeId")}>
          <input
            required
            disabled={isEdit}
            value={values.scheme_id}
            onChange={(e) => set("scheme_id", e.target.value)}
            className="input disabled:opacity-60"
            placeholder="e.g. state_farmer_grant_002"
          />
        </Field>
        <Field label={t("admin.schemeName")}>
          <input
            required
            value={values.scheme_name}
            onChange={(e) => set("scheme_name", e.target.value)}
            className="input"
          />
        </Field>
      </div>

      <Field label={t("admin.description")}>
        <textarea
          value={values.description}
          onChange={(e) => set("description", e.target.value)}
          className="input min-h-[70px]"
        />
      </Field>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Field label={t("benefits.category")}>
          <select value={values.category} onChange={(e) => set("category", e.target.value)} className="input">
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </Field>
        <Field label={t("admin.level")}>
          <select value={values.level} onChange={(e) => set("level", e.target.value)} className="input">
            <option value="Central">Central</option>
            <option value="State">State</option>
          </select>
        </Field>
        <Field label={t("admin.lastVerified")}>
          <input
            type="date"
            value={values.last_verified}
            onChange={(e) => set("last_verified", e.target.value)}
            className="input"
          />
        </Field>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label={t("admin.ministry")}>
          <input value={values.ministry} onChange={(e) => set("ministry", e.target.value)} className="input" />
        </Field>
        <Field label={t("admin.department")}>
          <input value={values.department} onChange={(e) => set("department", e.target.value)} className="input" />
        </Field>
      </div>

      <Field label={t("admin.applicableStates")}>
        <input
          value={values.applicable_states}
          onChange={(e) => set("applicable_states", e.target.value)}
          className="input"
          placeholder="Tamil Nadu, Kerala  (or: All States)"
        />
      </Field>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label={t("admin.officialUrl")}>
          <input
            type="url"
            value={values.official_url}
            onChange={(e) => set("official_url", e.target.value)}
            className="input"
          />
        </Field>
        <Field label={t("admin.sourceUrl")}>
          <input
            type="url"
            value={values.source_url}
            onChange={(e) => set("source_url", e.target.value)}
            className="input"
          />
        </Field>
      </div>
      <Field label={t("admin.sourceName")}>
        <input value={values.source_name} onChange={(e) => set("source_name", e.target.value)} className="input" />
      </Field>

      <Field label={t("scheme.benefits") + t("admin.oneLine")}>
        <textarea value={values.benefits} onChange={(e) => set("benefits", e.target.value)} className="input min-h-[70px]" />
      </Field>
      <Field label={t("scheme.requiredDocuments") + t("admin.oneLine")}>
        <textarea
          value={values.required_documents}
          onChange={(e) => set("required_documents", e.target.value)}
          className="input min-h-[70px]"
        />
      </Field>
      <Field label={t("scheme.howToApply") + t("admin.oneLine")}>
        <textarea
          value={values.application_steps}
          onChange={(e) => set("application_steps", e.target.value)}
          className="input min-h-[90px]"
        />
      </Field>

      <Field label={t("admin.eligibilityRulesJson")}>
        <textarea
          value={values.eligibility_rules_json}
          onChange={(e) => set("eligibility_rules_json", e.target.value)}
          className="input min-h-[140px] font-mono text-xs"
          spellCheck={false}
        />
        {jsonError && <p className="mt-1 text-xs text-[var(--danger)]">{jsonError}</p>}
        <p className="mt-1 text-xs text-[var(--ink-muted)]">{t("admin.eligibilityRulesHint")}</p>
      </Field>

      <Field label={t("admin.translationsJson")}>
        <textarea
          value={values.translations_json}
          onChange={(e) => set("translations_json", e.target.value)}
          className="input min-h-[140px] font-mono text-xs"
          spellCheck={false}
        />
        <p className="mt-1 text-xs text-[var(--ink-muted)]">{t("admin.translationsHint")}</p>
      </Field>

      <label className="flex items-center gap-2 text-sm font-semibold text-[var(--ink)]">
        <input type="checkbox" checked={values.is_demo} onChange={(e) => set("is_demo", e.target.checked)} />
        {t("admin.isDemo")}
      </label>

      {submitError && <p className="rounded-xl bg-[var(--danger-weak)] p-3 text-sm text-[var(--danger)]">{submitError}</p>}

      <div className="flex gap-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? t("admin.saving") : t("admin.save")}
        </Button>
        <Button type="button" variant="secondary" onClick={onCancel}>
          {t("accessibility.signInputCancel")}
        </Button>
      </div>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-semibold text-[var(--ink-muted)]">{label}</span>
      {children}
    </label>
  );
}
