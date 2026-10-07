import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./locales/en.json";
import hi from "./locales/hi.json";
import ta from "./locales/ta.json";

// Language choice is owned by App.tsx's own state (persisted under the
// "bn_language" localStorage key alongside every other app preference) and
// pushed into i18next via i18n.changeLanguage() — so no separate browser
// language-detector plugin is used here, avoiding two sources of truth.
i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    hi: { translation: hi },
    ta: { translation: ta },
  },
  lng: "en",
  fallbackLng: "en",
  supportedLngs: ["en", "hi", "ta"],
  interpolation: { escapeValue: false },
});

export default i18n;
