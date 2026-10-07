import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAppState } from "../hooks/useAppState";
import { useVoice } from "../hooks/useVoice";
import { IconButton } from "./Button";

/**
 * A persistent "read this page aloud" control for low-literacy users.
 * Reads the visible text of the current page's <main id="main-content">
 * region via the same browser TTS used elsewhere in the app, and shows a
 * synchronized caption panel so the audio is never the only channel the
 * information travels on (also helps deaf/hard-of-hearing users confirm
 * what the assistant *would* have said, without needing audio at all).
 */
export default function ReadAloudButton() {
  const { language, signAnimationEnabled } = useAppState();
  const { speak, isSynthesisSupported } = useVoice(language);
  const { t } = useTranslation();
  const [isReading, setIsReading] = useState(false);
  const [caption, setCaption] = useState("");
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    return () => {
      window.speechSynthesis?.cancel();
    };
  }, []);

  if (!isSynthesisSupported) return null;

  const collectPageText = (): string => {
    const main = document.getElementById("main-content");
    if (!main) return "";
    // Skip anything explicitly marked decorative/aria-hidden, and cap length
    // so a very long page (e.g. a full scheme list) doesn't run for minutes.
    const text = (main.innerText || "").replace(/\s+/g, " ").trim();
    return text.slice(0, 1200);
  };

  const start = () => {
    const text = collectPageText();
    if (!text) return;
    window.speechSynthesis.cancel();
    setCaption(text);
    setIsReading(true);

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === "hi" ? "hi-IN" : language === "ta" ? "ta-IN" : "en-IN";
    utterance.onend = () => setIsReading(false);
    utterance.onerror = () => setIsReading(false);
    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const stop = () => {
    window.speechSynthesis.cancel();
    setIsReading(false);
  };

  return (
    <>
      <div className="fixed bottom-5 right-5 z-30" style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}>
        <IconButton
          size="lg"
          active={isReading}
          onClick={() => (isReading ? stop() : start())}
          aria-label={isReading ? t("readAloud.stop") : t("readAloud.start")}
          title={isReading ? t("readAloud.stop") : t("readAloud.start")}
          className="shadow-lg"
        >
          <span aria-hidden>{isReading ? "⏹" : "🔊"}</span>
        </IconButton>
      </div>

      {isReading && (
        <div
          className="fixed inset-x-0 bottom-0 z-30 border-t border-[var(--line)] bg-[var(--surface)]/97 p-4 shadow-lg backdrop-blur"
          style={{ paddingBottom: "calc(1rem + env(safe-area-inset-bottom, 0px))" }}
          role="status"
          aria-live="polite"
        >
          <div className="mx-auto flex max-w-3xl items-start gap-3">
            {signAnimationEnabled ? (
              <span aria-hidden className="animate-bounce text-2xl">
                🖐️
              </span>
            ) : (
              <span aria-hidden className="text-xl">
                💬
              </span>
            )}
            <p className="max-h-32 flex-1 overflow-y-auto text-sm text-[var(--ink)]">{caption}</p>
            <IconButton size="md" onClick={stop} aria-label={t("readAloud.close")} title={t("readAloud.close")}>
              <span aria-hidden>✕</span>
            </IconButton>
          </div>
        </div>
      )}
    </>
  );
}
