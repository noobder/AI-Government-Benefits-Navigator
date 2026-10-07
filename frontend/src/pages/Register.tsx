import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { authApi } from "../services/auth";
import { useAppState } from "../hooks/useAppState";
import { Button } from "../components/Button";

export default function Register() {
  const { setAccount } = useAppState();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError(t("auth.passwordTooShort"));
      return;
    }
    setIsSubmitting(true);
    try {
      const account = await authApi.register(email, password);
      setAccount(account);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.genericError"));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-sm px-4 py-12">
      <h1 className="text-2xl font-bold text-[var(--ink)]">{t("auth.registerTitle")}</h1>
      <p className="mt-1 text-sm text-[var(--ink-muted)]">{t("auth.registerSubtitle")}</p>

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
            minLength={8}
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
          />
          <span className="mt-1 block text-xs text-[var(--ink-muted)]">{t("auth.passwordHint")}</span>
        </label>

        {error && <p className="rounded-xl bg-[var(--danger-weak)] p-3 text-sm text-[var(--danger)]">{error}</p>}

        <Button type="submit" size="lg" fullWidth disabled={isSubmitting}>
          {isSubmitting ? t("auth.creatingAccount") : t("auth.createAccount")}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-[var(--ink-muted)]">
        {t("auth.haveAccount")}{" "}
        <Link to="/login" className="font-semibold text-brand-700 underline">
          {t("auth.signIn")}
        </Link>
      </p>
      <p className="mt-2 text-center text-xs text-[var(--ink-muted)]">{t("auth.guestNotice")}</p>
    </div>
  );
}
