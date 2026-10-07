import { useTranslation } from "react-i18next";
import { useAppState } from "../hooks/useAppState";
import { useVoice } from "../hooks/useVoice";
import { IconButton } from "./Button";

export default function VoiceButton({
  onResult,
  size = "md",
}: {
  onResult: (text: string) => void;
  size?: "md" | "lg";
}) {
  const { language } = useAppState();
  const { isListening, isSupported, interimTranscript, error, listen, stopListening } = useVoice(language);
  const { t } = useTranslation();

  return (
    <div className="flex flex-col items-center gap-1">
      <IconButton
        type="button"
        onClick={() => (isListening ? stopListening() : listen(onResult))}
        disabled={!isSupported}
        active={isListening}
        size={size}
        aria-pressed={isListening}
        aria-label={isListening ? t("voice.stopInput") : t("voice.startInput")}
        title={isSupported ? t("voice.speakPrompt") : t("voice.notSupportedTitle")}
        className={isListening ? "animate-pulse !border-[var(--danger)] !bg-[var(--danger-weak)] !text-[var(--danger)]" : ""}
      >
        <span aria-hidden>🎤</span>
      </IconButton>

      {isListening && (
        <p className="max-w-[12rem] text-center text-xs font-medium text-[var(--ink-muted)]" role="status" aria-live="polite">
          {interimTranscript ? `"${interimTranscript}"` : t("voice.listening")}
        </p>
      )}
      {!isSupported && <p className="text-xs text-[var(--ink-muted)]">{t("voice.notSupported")}</p>}
      {error && (
        <p className="max-w-[12rem] text-center text-xs text-[var(--danger)]" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
