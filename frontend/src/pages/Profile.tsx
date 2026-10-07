import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ProfileForm from "../components/ProfileForm";
import { useAppState } from "../hooks/useAppState";
import { profileApi } from "../services/profile";
import type { UserProfile } from "../types/user";

export default function Profile() {
  const { profile, setProfile, userId, setUserId, language } = useAppState();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (values: UserProfile) => {
    setIsSaving(true);
    setError(null);
    try {
      let saved: UserProfile;
      if (userId) {
        saved = await profileApi.patch(userId, values as Record<string, unknown>);
      } else {
        saved = await profileApi.create({ ...values, language });
        if (saved.id) setUserId(saved.id);
      }
      setProfile(saved);
      navigate("/benefits");
    } catch (e) {
      setError(e instanceof Error ? e.message : t("profilePage.saveError"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold text-[var(--ink)]">{t("profilePage.heading")}</h1>
      <p className="mt-1 text-sm text-[var(--ink-muted)]">{t("profilePage.subtext")}</p>

      {error && <p className="mt-4 rounded-xl bg-[var(--danger-weak)] p-3 text-sm text-[var(--danger)]">{error}</p>}

      <div className="mt-6 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-6">
        <ProfileForm initial={profile} onSubmit={handleSubmit} isSaving={isSaving} />
      </div>
    </div>
  );
}
