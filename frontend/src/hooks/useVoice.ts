import { useCallback, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

const SPEECH_LANG: Record<string, string> = {
  en: "en-IN",
  hi: "hi-IN",
  ta: "ta-IN",
};

/**
 * Browser-based voice input/output (Web Speech API). This is the primary
 * voice path for the app: it needs no backend or API key and already
 * supports English, Hindi, and Tamil in Chromium browsers. If unsupported,
 * `isSupported` is false and the UI should fall back to text input.
 *
 * `interimResults` is intentionally on: without it, Chrome only ever fires
 * `onresult` after it decides an utterance is fully finished, which for a
 * short phrase or a noisy mic can simply never happen — producing total
 * silence with no error. With it on, the caller gets live, progressively
 * updated text as the user speaks, so voice input visibly "does something"
 * even if the browser never finalizes the utterance.
 */
export function useVoice(language: string) {
  const { t } = useTranslation();
  const [isListening, setIsListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);
  const finalTranscriptRef = useRef("");
  const gotAnyResultRef = useRef(false);
  const hadErrorRef = useRef(false);

  const speechLang = SPEECH_LANG[language] ?? "en-IN";

  const SpeechRecognitionCtor =
    typeof window !== "undefined" &&
    ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
  const isSupported = Boolean(SpeechRecognitionCtor);
  const isSynthesisSupported = typeof window !== "undefined" && "speechSynthesis" in window;
  const isSecureContext = typeof window === "undefined" || window.isSecureContext !== false;

  const listen = useCallback(
    (onResult: (text: string) => void) => {
      if (!SpeechRecognitionCtor) {
        setError(t("voice.errorNotSupportedBrowser"));
        return;
      }
      if (!isSecureContext) {
        setError(t("voice.errorInsecureContext"));
        return;
      }

      setError(null);
      setInterimTranscript("");
      finalTranscriptRef.current = "";
      gotAnyResultRef.current = false;
      hadErrorRef.current = false;

      const recognition = new SpeechRecognitionCtor();
      recognition.lang = speechLang;
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setIsListening(true);

      recognition.onerror = (e: any) => {
        setIsListening(false);
        hadErrorRef.current = true;
        const reason = e?.error;
        const messages: Record<string, string> = {
          "not-allowed": t("voice.errorNotAllowed"),
          "no-speech": t("voice.errorNoSpeech"),
          "audio-capture": t("voice.errorNoMic"),
          "language-not-supported": t("voice.errorLanguageNotSupported"),
          network: t("voice.errorNetwork"),
        };
        // "aborted" fires when we call stopListening() ourselves — not a real
        // failure, so it shouldn't show an error at all.
        if (reason === "aborted") return;
        setError(messages[reason] ?? t("voice.errorGeneric"));
      };

      recognition.onresult = (event: any) => {
        let interim = "";
        let final = finalTranscriptRef.current;
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const chunk = event.results[i][0]?.transcript ?? "";
          if (event.results[i].isFinal) {
            final = `${final} ${chunk}`.trim();
          } else {
            interim += chunk;
          }
        }
        finalTranscriptRef.current = final;
        setInterimTranscript(interim);
        gotAnyResultRef.current = true;
        onResult(`${final} ${interim}`.trim());
      };

      recognition.onend = () => {
        setIsListening(false);
        setInterimTranscript("");
        // Only fall back to the generic "didn't catch that" message when
        // onerror never fired with a more specific, actionable reason —
        // otherwise this unconditionally clobbered it on every failure.
        if (!gotAnyResultRef.current && !hadErrorRef.current) {
          setError(t("voice.errorDidntCatch"));
        }
      };

      recognitionRef.current = recognition;
      try {
        recognition.start();
      } catch {
        setIsListening(false);
        setError(t("voice.errorCouldNotStart"));
      }
    },
    [SpeechRecognitionCtor, isSecureContext, speechLang, t]
  );

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  const speak = useCallback(
    (text: string) => {
      if (!isSynthesisSupported || !text) return;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = speechLang;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    },
    [isSynthesisSupported, speechLang]
  );

  return {
    isListening,
    isSupported,
    isSynthesisSupported,
    isSecureContext,
    interimTranscript,
    error,
    listen,
    stopListening,
    speak,
  };
}
