import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAppState } from "../hooks/useAppState";
import { useVoice } from "../hooks/useVoice";
import { helpApi, type TutorialStep } from "../services/help";
import { Button, IconButton } from "./Button";

type Mode = "menu" | "tour" | "ask";

interface AskMessage {
  role: "user" | "assistant";
  text: string;
}

export default function HelpPanel() {
  const { t } = useTranslation();
  const { language } = useAppState();
  const { speak, isSynthesisSupported } = useVoice(language);
  const navigate = useNavigate();

  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<Mode>("menu");

  const [steps, setSteps] = useState<TutorialStep[]>([]);
  const [stepIndex, setStepIndex] = useState(0);

  const [messages, setMessages] = useState<AskMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [isAsking, setIsAsking] = useState(false);

  const spokenStepRef = useRef<string | null>(null);

  const startTour = async () => {
    const tutorialSteps = await helpApi.tutorial(language);
    setSteps(tutorialSteps);
    setStepIndex(0);
    setMode("tour");
  };

  useEffect(() => {
    if (mode !== "tour" || steps.length === 0) return;
    const step = steps[stepIndex];
    if (step.route) navigate(step.route);
    if (isSynthesisSupported && spokenStepRef.current !== step.step_id) {
      spokenStepRef.current = step.step_id;
      speak(step.narration);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, stepIndex, steps]);

  const askQuestion = async (text: string) => {
    setMessages((m) => [...m, { role: "user", text }]);
    setIsAsking(true);
    try {
      const resp = await helpApi.ask(text, language);
      setMessages((m) => [...m, { role: "assistant", text: resp.answer }]);
      if (isSynthesisSupported) speak(resp.answer);
    } finally {
      setIsAsking(false);
    }
  };

  const close = () => {
    window.speechSynthesis?.cancel();
    setOpen(false);
    setMode("menu");
  };

  return (
    <>
      <div className="fixed bottom-5 left-5 z-30" style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}>
        <IconButton size="lg" onClick={() => setOpen(true)} aria-label={t("help.open")} title={t("help.open")} className="shadow-lg">
          <span aria-hidden>❓</span>
        </IconButton>
      </div>

      {open && (
        <div className="fixed inset-0 z-40 flex items-end justify-start p-4 sm:items-center" role="dialog" aria-modal="true" aria-label={t("help.title")}>
          <div className="absolute inset-0 bg-black/40" onClick={close} aria-hidden />
          <div className="relative z-10 w-full max-w-md rounded-2xl bg-[var(--surface)] p-5 shadow-xl">
            <div className="flex items-start justify-between">
              <h2 className="text-lg font-bold text-[var(--ink)]">{t("help.title")}</h2>
              <button onClick={close} aria-label={t("help.close")} className="text-xl text-[var(--ink-muted)]">
                ✕
              </button>
            </div>

            {mode === "menu" && (
              <div className="mt-4 space-y-2">
                <Button fullWidth onClick={startTour}>
                  {t("help.startTour")}
                </Button>
                <Button fullWidth variant="secondary" onClick={() => setMode("ask")}>
                  {t("help.askQuestion")}
                </Button>
              </div>
            )}

            {mode === "tour" && steps.length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-muted)]">
                  {t("help.step", { current: stepIndex + 1, total: steps.length })}
                </p>
                <h3 className="mt-1 text-base font-bold text-[var(--ink)]">{steps[stepIndex].title}</h3>
                <p className="mt-2 max-h-40 overflow-y-auto text-sm text-[var(--ink)]" role="status" aria-live="polite">
                  {steps[stepIndex].narration}
                </p>
                <div className="mt-4 flex gap-2">
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => setStepIndex((i) => Math.max(0, i - 1))}
                    disabled={stepIndex === 0}
                  >
                    {t("help.back")}
                  </Button>
                  {stepIndex < steps.length - 1 ? (
                    <Button type="button" onClick={() => setStepIndex((i) => i + 1)}>
                      {t("help.next")}
                    </Button>
                  ) : (
                    <Button type="button" onClick={close}>
                      {t("help.done")}
                    </Button>
                  )}
                </div>
              </div>
            )}

            {mode === "ask" && (
              <div className="mt-4">
                <div className="max-h-64 space-y-2 overflow-y-auto">
                  {messages.length === 0 && (
                    <p className="text-sm text-[var(--ink-muted)]">{t("help.askPrompt")}</p>
                  )}
                  {messages.map((m, i) => (
                    <div
                      key={i}
                      className={`rounded-xl p-3 text-sm ${
                        m.role === "user" ? "bg-brand-700 text-white" : "border border-[var(--line)] bg-[var(--surface-2)] text-[var(--ink)]"
                      }`}
                    >
                      {m.text}
                    </div>
                  ))}
                  {isAsking && <p className="text-sm text-[var(--ink-muted)]">{t("chat.thinking")}</p>}
                </div>
                <form
                  className="mt-3 flex gap-2"
                  onSubmit={(e) => {
                    e.preventDefault();
                    const text = draft.trim();
                    if (!text) return;
                    setDraft("");
                    askQuestion(text);
                  }}
                >
                  <input
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    placeholder={t("help.askPlaceholder")}
                    className="input"
                  />
                  <Button type="submit" disabled={!draft.trim()}>
                    {t("chat.send")}
                  </Button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
