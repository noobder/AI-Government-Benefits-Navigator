import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import VoiceButton from "../components/VoiceButton";
import { useAppState } from "../hooks/useAppState";

// `key` matches the scheme.category value from the backend (always English,
// since it's structured data) — only the displayed label is translated.
const CATEGORIES = [
  { emoji: "🎓", key: "Education" },
  { emoji: "🌾", key: "Agriculture" },
  { emoji: "💰", key: "Financial Assistance" },
  { emoji: "🏠", key: "Housing" },
  { emoji: "💼", key: "Employment" },
  { emoji: "👩", key: "Women" },
  { emoji: "♿", key: "Disability" },
  { emoji: "👴", key: "Senior Citizens" },
  { emoji: "🏥", key: "Healthcare" },
  { emoji: "🏪", key: "Business" },
];

export default function Home() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { simpleMode } = useAppState();

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <section className="rounded-3xl bg-gradient-to-br from-brand-700 to-brand-900 px-6 py-12 text-center text-white shadow-lg">
        <h1
          className={`mx-auto max-w-2xl font-extrabold leading-tight ${simpleMode ? "text-4xl sm:text-5xl" : "text-3xl sm:text-4xl"}`}
        >
          {t("home.headline")}
        </h1>
        {!simpleMode && <p className="mx-auto mt-4 max-w-xl text-base text-brand-50">{t("home.subheadline")}</p>}

        <div className={`mt-8 flex flex-wrap items-center justify-center gap-3 ${simpleMode ? "flex-col" : ""}`}>
          <Link
            to="/profile"
            className={`rounded-xl bg-white font-bold text-brand-800 shadow hover:bg-brand-50 ${
              simpleMode ? "w-full max-w-sm px-8 py-6 text-xl" : "px-6 py-4 text-base"
            }`}
          >
            {t("home.findMyBenefits")}
          </Link>
          <Link
            to="/chat"
            className={`rounded-xl border-2 border-white font-bold text-white hover:bg-white/10 ${
              simpleMode ? "w-full max-w-sm px-8 py-6 text-xl" : "px-6 py-4 text-base"
            }`}
          >
            {t("home.askAQuestion")}
          </Link>
          <div
            className={`flex items-center gap-3 rounded-xl border-2 border-white px-4 ${
              simpleMode ? "w-full max-w-sm justify-center py-3" : "py-2"
            }`}
          >
            <span className={simpleMode ? "text-lg font-bold" : "text-sm font-bold"}>{t("home.speakToAi")}</span>
            <VoiceButton
              size="md"
              onResult={(text) => navigate("/chat", { state: { initialMessage: text } })}
            />
          </div>
        </div>
      </section>

      <section className="mt-10">
        <h2 className="mb-4 text-xl font-bold text-[var(--ink)]">{t("home.browseByCategory")}</h2>
        <div
          className={`grid gap-3 ${simpleMode ? "grid-cols-2 sm:grid-cols-3" : "grid-cols-2 sm:grid-cols-3 md:grid-cols-5"}`}
        >
          {CATEGORIES.map((c) => (
            <Link
              key={c.key}
              to={`/benefits?category=${encodeURIComponent(c.key)}`}
              className={`flex flex-col items-center justify-center gap-2 rounded-2xl border border-[var(--line)] bg-[var(--surface)] text-center shadow-sm transition hover:border-brand-400 hover:shadow ${
                simpleMode ? "min-h-[140px] p-6" : "min-h-[96px] p-4"
              }`}
            >
              <span className={simpleMode ? "text-5xl" : "text-3xl"} aria-hidden>
                {c.emoji}
              </span>
              <span className={`font-semibold text-[var(--ink)] ${simpleMode ? "text-base" : "text-sm"}`}>
                {t(`common.category.${c.key}`)}
              </span>
            </Link>
          ))}
        </div>
      </section>

      {!simpleMode && (
        <section className="mt-10 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-6">
          <h2 className="text-lg font-bold text-[var(--ink)]">{t("home.whyTrust")}</h2>
          <ul className="mt-3 space-y-2 text-sm text-[var(--ink-muted)]">
            <li>✔ {t("home.trust1")}</li>
            <li>✔ {t("home.trust2")}</li>
            <li>✔ {t("home.trust3")}</li>
            <li>✔ {t("home.trust4")}</li>
          </ul>
        </section>
      )}
    </div>
  );
}
