import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import ReadAloudButton from "./components/ReadAloudButton";
import HelpPanel from "./components/HelpPanel";
import Welcome from "./components/Welcome";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import Profile from "./pages/Profile";
import Benefits from "./pages/Benefits";
import SchemeDetails from "./pages/SchemeDetails";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Admin from "./pages/Admin";
import { AppContext, type Theme } from "./hooks/useAppState";
import type { UserProfile } from "./types/user";
import type { Account } from "./types/auth";
import { authApi } from "./services/auth";

function useLocalStorageState<T>(key: string, initial: T): [T, (v: T) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : initial;
    } catch {
      return initial;
    }
  });
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* ignore storage errors (private browsing, quota) */
    }
  }, [key, value]);
  return [value, setValue];
}

export default function App() {
  const [userId, setUserId] = useLocalStorageState<string | null>("bn_user_id", null);
  const [language, setLanguage] = useLocalStorageState<string>("bn_language", "en");
  const [profile, setProfile] = useLocalStorageState<UserProfile>("bn_profile", {});
  const [largeText, setLargeText] = useLocalStorageState<boolean>("bn_large_text", false);
  const [highContrast, setHighContrast] = useLocalStorageState<boolean>("bn_high_contrast", false);
  const [theme, setTheme] = useLocalStorageState<Theme>("bn_theme", "system");
  const [simpleMode, setSimpleMode] = useLocalStorageState<boolean>("bn_simple_mode", false);
  const [signInputEnabled, setSignInputEnabled] = useLocalStorageState<boolean>("bn_sign_input", false);
  const [signAnimationEnabled, setSignAnimationEnabled] = useLocalStorageState<boolean>("bn_sign_animation", false);
  const [welcomed, setWelcomed] = useLocalStorageState<boolean>("bn_welcomed", false);
  const [account, setAccount] = useState<Account | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const { i18n } = useTranslation();

  useEffect(() => {
    i18n.changeLanguage(language);
    document.documentElement.lang = language;
  }, [language, i18n]);

  useEffect(() => {
    // data-theme lives on <html> since index.css keys the palette off :root,
    // and :root is the document element, not any wrapper div.
    const root = document.documentElement;
    if (theme === "system") {
      root.removeAttribute("data-theme");
    } else {
      root.setAttribute("data-theme", theme);
    }
  }, [theme]);

  useEffect(() => {
    // Tailwind's text-* utilities are rem-based, so they only respond to the
    // root <html> font-size, not an em-scaled ancestor div — set it here.
    document.documentElement.style.fontSize = largeText ? "18px" : "";
  }, [largeText]);

  useEffect(() => {
    // Restore session from the httpOnly cookie on first load, if any —
    // guest usage (account stays null) is the normal, unauthenticated path.
    authApi
      .me()
      .then(setAccount)
      .catch(() => setAccount(null))
      .finally(() => setAuthLoading(false));
  }, []);

  return (
    <AppContext.Provider
      value={{
        userId,
        setUserId,
        account,
        setAccount,
        authLoading,
        language,
        setLanguage,
        profile,
        setProfile,
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
      }}
    >
      <div className={`min-h-screen ${highContrast ? "high-contrast" : ""} ${simpleMode ? "simple-mode" : ""}`}>
        <BrowserRouter>
          {!welcomed ? (
            <Welcome onContinue={() => setWelcomed(true)} />
          ) : (
            <>
              <Header />
              <main id="main-content">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/chat" element={<Chat />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/benefits" element={<Benefits />} />
                  <Route path="/schemes/:schemeId" element={<SchemeDetails />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/admin" element={<Admin />} />
                </Routes>
              </main>
              <ReadAloudButton />
              <HelpPanel />
            </>
          )}
        </BrowserRouter>
      </div>
    </AppContext.Provider>
  );
}
