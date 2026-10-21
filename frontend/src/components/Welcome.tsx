import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "./Button";
import LanguageSelector from "./LanguageSelector";

/**
 * First-run splash screen: describes what the app does before dropping the
 * user into the main app. Shown once per device (gated by the "welcomed"
 * flag App.tsx persists to localStorage) — returning users go straight to
 * the main page, this is purely a one-time introduction, not a route.
 */
export default function Welcome({ onContinue }: { onContinue: () => void }) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const goToSignIn = () => {
    onContinue();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-brand-700 to-brand-900 text-white">
      <div className="flex justify-end p-4">
        <LanguageSelector />
      </div>

      <div className="flex flex-1 flex-col items-center justify-center px-6 py-10 text-center">
        <span aria-hidden className="text-6xl">
          🏛️
        </span>
        <h1 className="mt-4 text-3xl font-extrabold sm:text-4xl">{t("welcome.title")}</h1>
        <p className="mt-3 max-w-md text-lg font-semibold text-brand-50">{t("welcome.tagline")}</p>
        <p className="mt-4 max-w-md text-sm text-brand-100">{t("welcome.description")}</p>

        <ul className="mt-6 max-w-md space-y-2 text-left text-sm text-brand-50">
          <li>✔ {t("home.trust1")}</li>
          <li>✔ {t("home.trust2")}</li>
          <li>✔ {t("home.trust3")}</li>
        </ul>

        <div className="mt-10 flex w-full max-w-xs flex-col items-stretch gap-3">
          <Button
            size="lg"
            onClick={onContinue}
            className="!bg-white !text-brand-800 hover:!bg-brand-50"
          >
            {t("welcome.letsGo")}
          </Button>
          <p className="text-xs text-brand-100">{t("welcome.continueAsGuest")}</p>
        </div>

        <div className="mt-8 border-t border-white/20 pt-6 text-sm">
          <span className="text-brand-100">{t("welcome.alreadySignedUp")}</span>{" "}
          <button onClick={goToSignIn} className="font-bold text-white underline underline-offset-2">
            {t("welcome.signIn")}
          </button>
        </div>
      </div>
    </div>
  );
}
