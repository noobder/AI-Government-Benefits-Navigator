import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { authApi } from "../services/auth";
import { useAppState } from "../hooks/useAppState";
import { Button } from "../components/Button";

export default function Login() {
  const { setAccount } = useAppState();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation() as { state?: { from?: string } };
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const account = await authApi.login(email, password);
      setAccount(account);
      navigate(location.state?.from ?? "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.genericError"));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-sm px-4 py-12">
      <h1 className="text-2xl font-bold text-[var(--ink)]">{t("auth.loginTitle")}</h1>
      <p className="mt-1 text-sm text-[var(--ink-muted)]">{t("auth.loginSubtitle")}</p>

      <form className="mt-6 space-y-4" onSubmit={submit}>
        <label className="block">
          <span className="mb-1 block text-sm font-semibold text-[var(--ink-muted)]">{t("auth.email")}</span>
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-sm font-semibold text-[var(--ink-muted)]">{t("auth.password")}</span>
          <input
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
          />
        </label>

        {error && <p className="rounded-xl bg-[var(--danger-weak)] p-3 text-sm text-[var(--danger)]">{error}</p>}

        <Button type="submit" size="lg" fullWidth disabled={isSubmitting}>
          {isSubmitting ? t("auth.signingIn") : t("auth.signIn")}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-[var(--ink-muted)]">
        {t("auth.noAccount")}{" "}
        <Link to="/register" className="font-semibold text-brand-700 underline">
          {t("auth.createOne")}
        </Link>
      </p>
      <p className="mt-2 text-center text-xs text-[var(--ink-muted)]">{t("auth.guestNotice")}</p>
    </div>
  );
}
