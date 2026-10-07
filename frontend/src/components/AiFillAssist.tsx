import { useState } from "react";
import { useTranslation } from "react-i18next";
import { profileApi } from "../services/profile";
import { Button } from "./Button";
import VoiceButton from "./VoiceButton";
import type { UserProfile } from "../types/user";

/**
 * "Fill with AI" — lets someone describe themselves once (typed or spoken)
 * instead of tabbing through every field. Reuses the same extraction logic
 * the chat assistant uses (POST /api/profile/extract -> profile_service),
 * so it never fabricates a value the form itself wouldn't. The user always
 * sees exactly what was filled and reviews it before submitting.
 */
export default function AiFillAssist({ onFilled }: { onFilled: (fields: Partial<UserProfile>) => void }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [isExtracting, setIsExtracting] = useState(false);
  const [filledCount, setFilledCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runExtract = async () => {
    if (!text.trim()) return;
    setIsExtracting(true);
    setError(null);
    setFilledCount(null);
    try {
      const fields = await profileApi.extract(text);
      const nonEmpty = Object.fromEntries(Object.entries(fields).filter(([, v]) => v !== null && v !== undefined));
      onFilled(nonEmpty);
      setFilledCount(Object.keys(nonEmpty).length);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.genericError"));
    } finally {
      setIsExtracting(false);
    }
  };

  if (!open) {
    return (
      <Button type="button" variant="secondary" onClick={() => setOpen(true)}>
        {t("profileForm.fillWithAi")}
      </Button>
    );
  }

  return (
    <div className="rounded-xl border border-[var(--line)] bg-[var(--surface-2)] p-4">
      <p className="text-sm font-semibold text-[var(--ink)]">{t("profileForm.fillWithAiPrompt")}</p>
      <div className="mt-2 flex items-start gap-2">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="input min-h-[80px] flex-1"
          placeholder={t("profileForm.fillWithAiPlaceholder")}
        />
        <VoiceButton onResult={(spoken) => setText(spoken)} />
      </div>

      {error && <p className="mt-2 text-sm text-[var(--danger)]">{error}</p>}
      {filledCount !== null && (
        <p className="mt-2 text-sm text-[var(--brand)]">{t("profileForm.fillWithAiFilled", { count: filledCount })}</p>
      )}

      <div className="mt-3 flex gap-2">
        <Button type="button" onClick={runExtract} disabled={isExtracting || !text.trim()}>
          {isExtracting ? t("profileForm.fillWithAiWorking") : t("profileForm.fillWithAiSubmit")}
        </Button>
        <Button type="button" variant="secondary" onClick={() => setOpen(false)}>
          {t("accessibility.signInputCancel")}
        </Button>
      </div>
    </div>
  );
}
