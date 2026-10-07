import { lazy, Suspense, useState } from "react";
import { useTranslation } from "react-i18next";
import type { UserProfile } from "../types/user";
import { Button } from "./Button";
import AiFillAssist from "./AiFillAssist";
import { useAppState } from "../hooks/useAppState";

// The MediaPipe hand-tracking library this pulls in is large; load it only
// for the small fraction of users who turn on the experimental sign-input
// setting, instead of shipping it in everyone's main bundle.
const SignInputButton = lazy(() => import("./SignInputButton"));

const INDIAN_STATES = [
  "Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh", "Telangana", "Maharashtra",
  "Gujarat", "Rajasthan", "Punjab", "Uttar Pradesh", "West Bengal", "Bihar", "Odisha", "Madhya Pradesh",
];

export default function ProfileForm({
  initial,
  onSubmit,
  isSaving = false,
}: {
  initial?: UserProfile;
  onSubmit: (profile: UserProfile) => void;
  isSaving?: boolean;
}) {
  const [profile, setProfile] = useState<UserProfile>(initial ?? {});
  const { t } = useTranslation();
  const { signInputEnabled } = useAppState();

  const set = <K extends keyof UserProfile>(key: K, value: UserProfile[K]) =>
    setProfile((p) => ({ ...p, [key]: value }));

  return (
    <form
      className="space-y-5"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(profile);
      }}
    >
      <p className="text-sm text-[var(--ink-muted)]">{t("profileForm.intro")}</p>

      <AiFillAssist onFilled={(fields) => setProfile((p) => ({ ...p, ...fields }))} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label={t("profileForm.age")}>
          <input
            type="number"
            min={0}
            max={120}
            value={profile.age ?? ""}
            onChange={(e) => set("age", e.target.value ? Number(e.target.value) : null)}
            className="input"
          />
        </Field>

        <Field label={t("profileForm.gender")}>
          <select value={profile.gender ?? ""} onChange={(e) => set("gender", e.target.value || null)} className="input">
            <option value="">{t("profileForm.genderPreferNotToSay")}</option>
            <option value="female">{t("profileForm.genderFemale")}</option>
            <option value="male">{t("profileForm.genderMale")}</option>
            <option value="other">{t("profileForm.genderOther")}</option>
          </select>
        </Field>

        <Field label={t("profileForm.state")}>
          <select value={profile.state ?? ""} onChange={(e) => set("state", e.target.value || null)} className="input">
            <option value="">{t("profileForm.selectState")}</option>
            {INDIAN_STATES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </Field>

        <Field label={t("profileForm.district")}>
          <input
            type="text"
            value={profile.district ?? ""}
            onChange={(e) => set("district", e.target.value || null)}
            className="input"
          />
        </Field>

        <Field label={t("profileForm.areaType")}>
          <select
            value={profile.residence_type ?? ""}
            onChange={(e) => set("residence_type", e.target.value || null)}
            className="input"
          >
            <option value="">{t("profileForm.select")}</option>
            <option value="rural">{t("profileForm.rural")}</option>
            <option value="urban">{t("profileForm.urban")}</option>
          </select>
        </Field>

        <Field label={t("profileForm.occupation")}>
          <input
            type="text"
            placeholder={t("profileForm.occupationPlaceholder")}
            value={profile.occupation ?? ""}
            onChange={(e) => set("occupation", e.target.value || null)}
            className="input"
          />
        </Field>

        <Field label={t("profileForm.annualIncome")}>
          <input
            type="number"
            min={0}
            value={profile.annual_income ?? ""}
            onChange={(e) => set("annual_income", e.target.value ? Number(e.target.value) : null)}
            className="input"
          />
        </Field>

        <Field label={t("profileForm.familySize")}>
          <input
            type="number"
            min={1}
            value={profile.family_size ?? ""}
            onChange={(e) => set("family_size", e.target.value ? Number(e.target.value) : null)}
            className="input"
          />
        </Field>

        <Field label={t("profileForm.areYouStudent")}>
          <div className="flex items-center gap-2">
            <select
              value={profile.student === true ? "yes" : profile.student === false ? "no" : ""}
              onChange={(e) => set("student", e.target.value === "" ? null : e.target.value === "yes")}
              className="input"
            >
              <option value="">{t("profileForm.select")}</option>
              <option value="yes">{t("profileForm.yes")}</option>
              <option value="no">{t("profileForm.no")}</option>
            </select>
            {signInputEnabled && (
              <Suspense fallback={null}>
                <SignInputButton onYesNo={(v) => set("student", v)} />
              </Suspense>
            )}
          </div>
        </Field>

        {profile.student && (
          <>
            <Field label={t("profileForm.courseOfStudy")}>
              <input
                type="text"
                value={profile.course ?? ""}
                onChange={(e) => set("course", e.target.value || null)}
                className="input"
              />
            </Field>
            <Field label={t("profileForm.previousPercentage")}>
              <input
                type="number"
                min={0}
                max={100}
                value={profile.previous_academic_percentage ?? ""}
                onChange={(e) =>
                  set("previous_academic_percentage", e.target.value ? Number(e.target.value) : null)
                }
                className="input"
              />
            </Field>
          </>
        )}

        {profile.occupation?.toLowerCase().includes("farm") && (
          <>
            <Field label={t("profileForm.landOwnership")}>
              <select
                value={profile.land_ownership ?? ""}
                onChange={(e) => set("land_ownership", e.target.value || null)}
                className="input"
              >
                <option value="">{t("profileForm.select")}</option>
                <option value="owned">{t("profileForm.landOwned")}</option>
                <option value="leased">{t("profileForm.landLeased")}</option>
                <option value="family">{t("profileForm.landFamily")}</option>
                <option value="unknown">{t("profileForm.landUnknown")}</option>
              </select>
            </Field>
            <Field label={t("profileForm.landArea")}>
              <input
                type="number"
                min={0}
                step="0.1"
                value={profile.land_area_acres ?? ""}
                onChange={(e) => set("land_area_acres", e.target.value ? Number(e.target.value) : null)}
                className="input"
              />
            </Field>
          </>
        )}

        <Field label={t("profileForm.employmentStatus")}>
          <select
            value={profile.employment_status ?? ""}
            onChange={(e) => set("employment_status", e.target.value || null)}
            className="input"
          >
            <option value="">{t("profileForm.select")}</option>
            <option value="employed">{t("profileForm.employed")}</option>
            <option value="unemployed">{t("profileForm.unemployed")}</option>
            <option value="self-employed">{t("profileForm.selfEmployed")}</option>
            <option value="business owner">{t("profileForm.businessOwner")}</option>
            <option value="informal worker">{t("profileForm.informalWorker")}</option>
          </select>
        </Field>

        <Field label={t("profileForm.hasDisability")}>
          <div className="flex items-center gap-2">
            <select
              value={profile.disability_status === true ? "yes" : profile.disability_status === false ? "no" : ""}
              onChange={(e) => set("disability_status", e.target.value === "" ? null : e.target.value === "yes")}
              className="input"
            >
              <option value="">{t("profileForm.select")}</option>
              <option value="yes">{t("profileForm.yes")}</option>
              <option value="no">{t("profileForm.no")}</option>
            </select>
            {signInputEnabled && (
              <Suspense fallback={null}>
                <SignInputButton onYesNo={(v) => set("disability_status", v)} />
              </Suspense>
            )}
          </div>
        </Field>
      </div>

      <Button type="submit" size="lg" fullWidth className="shadow-sm" disabled={isSaving}>
        {isSaving ? t("profileForm.saving") : t("profileForm.submit")}
      </Button>
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
