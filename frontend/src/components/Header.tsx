import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageSelector from "./LanguageSelector";
import { useAppState, type Theme } from "../hooks/useAppState";
import { IconButton } from "./Button";
import { authApi } from "../services/auth";

const NAV = [
  { to: "/", key: "home" },
  { to: "/chat", key: "chat" },
  { to: "/profile", key: "profile" },
  { to: "/benefits", key: "benefits" },
] as const;

const THEME_ICON: Record<Theme, string> = { light: "☀️", dark: "🌙", system: "🖥️" };
const THEME_NEXT: Record<Theme, Theme> = { light: "dark", dark: "system", system: "light" };

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { largeText, setLargeText, highContrast, setHighContrast, theme, setTheme, account, setAccount } =
    useAppState();
  const { t } = useTranslation();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    await authApi.logout();
    setAccount(null);
    setMenuOpen(false);
    navigate("/");
  };

  const navLinkClass = (active: boolean) =>
    `flex min-h-[44px] items-center whitespace-nowrap rounded-xl px-3 text-sm font-semibold transition ${
      active ? "bg-brand-100 text-brand-800" : "text-[var(--ink-muted)] hover:bg-[var(--surface-2)]"
    }`;

  const navLinks = (
    <>
      {NAV.map((item) => (
        <Link
          key={item.to}
          to={item.to}
          onClick={() => setMenuOpen(false)}
          className={navLinkClass(location.pathname === item.to)}
        >
          {t(`common.nav.${item.key}`)}
        </Link>
      ))}
      {account?.role === "admin" && (
        <Link to="/admin" onClick={() => setMenuOpen(false)} className={navLinkClass(location.pathname === "/admin")}>
          {t("admin.title")}
        </Link>
      )}
    </>
  );

  const controls = (
    <>
      <IconButton
        onClick={() => setTheme(THEME_NEXT[theme])}
        aria-label={t(`common.theme.${theme}`)}
        title={t(`common.theme.${theme}`)}
      >
        <span aria-hidden>{THEME_ICON[theme]}</span>
      </IconButton>
      <IconButton
        onClick={() => setHighContrast(!highContrast)}
        aria-pressed={highContrast}
        active={highContrast}
        aria-label={t("common.toggleContrast")}
        title={t("common.toggleContrast")}
      >
        <span aria-hidden className="text-sm font-bold">CT</span>
      </IconButton>
      <IconButton
        onClick={() => setLargeText(!largeText)}
        aria-pressed={largeText}
        active={largeText}
        aria-label={t("common.toggleLargeText")}
        title={t("common.toggleLargeText")}
      >
        <span aria-hidden className="text-sm font-bold">A+</span>
      </IconButton>
      <LanguageSelector />

      <IconButton
        onClick={() => {
          setMenuOpen(false);
          navigate("/settings");
        }}
        active={location.pathname === "/settings"}
        aria-label={t("settings.title")}
        title={t("settings.title")}
      >
        <span aria-hidden>⚙️</span>
      </IconButton>

      {account ? (
        <div className="flex flex-shrink-0 items-center gap-2">
          <span className="hidden max-w-[9rem] truncate text-xs text-[var(--ink-muted)] sm:inline" title={account.email}>
            {account.email}
          </span>
          <button
            onClick={handleLogout}
            className="min-h-[44px] flex-shrink-0 whitespace-nowrap rounded-xl border border-[var(--line-strong)] px-3 text-sm font-semibold text-[var(--ink)] hover:bg-[var(--surface-2)]"
          >
            {t("auth.signOut")}
          </button>
        </div>
      ) : (
        <Link
          to="/login"
          onClick={() => setMenuOpen(false)}
          className="flex min-h-[44px] flex-shrink-0 items-center whitespace-nowrap rounded-xl border border-[var(--line-strong)] px-3 text-sm font-semibold text-[var(--ink)] hover:bg-[var(--surface-2)]"
        >
          {t("auth.signIn")}
        </Link>
      )}
    </>
  );

  return (
    <header className="sticky top-0 z-20 border-b border-[var(--line)] bg-[var(--surface)]/95 backdrop-blur">
      <div className="mx-auto max-w-5xl px-4 py-3">
        {/* Fixed-height bar: same on every screen size and every language, so
            switching languages never shifts the page (translated labels only
            affect the collapsible areas below, not this row's height). */}
        <div className="flex items-center justify-between gap-3">
          <Link to="/" className="flex flex-shrink-0 items-center gap-2 text-lg font-bold text-brand-700">
            <span aria-hidden>🏛️</span>
            <span>{t("common.appName")}</span>
          </Link>

          {/* Desktop: nav inline, always visible. lg (not md) so the widest
              translated labels (Tamil) still fit on one line without wrapping. */}
          <nav className="hidden flex-wrap items-center justify-end gap-1 lg:flex" aria-label="Main navigation">
            {navLinks}
          </nav>

          {/* Mobile/tablet: a single hamburger toggle keeps this row's height constant. */}
          <IconButton
            className="lg:hidden"
            onClick={() => setMenuOpen((v) => !v)}
            aria-expanded={menuOpen}
            aria-label={t("common.toggleMenu")}
            title={t("common.toggleMenu")}
          >
            <span aria-hidden>{menuOpen ? "✕" : "☰"}</span>
          </IconButton>
        </div>

        {/* Desktop: controls row, always visible, always its own line. */}
        <div className="mt-2 hidden flex-wrap items-center justify-end gap-2 lg:flex">{controls}</div>

        {/* Mobile/tablet: nav + controls collapse into this panel, opened
            deliberately by the hamburger rather than automatically by a
            language switch. */}
        {menuOpen && (
          <div className="mt-2 flex flex-col gap-1 border-t border-[var(--line)] pt-2 lg:hidden">
            {navLinks}
            <div className="mt-1 flex flex-wrap items-center gap-2 border-t border-[var(--line)] pt-2">{controls}</div>
          </div>
        )}
      </div>
    </header>
  );
}
