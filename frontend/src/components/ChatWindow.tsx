import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import MessageBubble, { type ChatMessage } from "./MessageBubble";
import VoiceButton from "./VoiceButton";
import { Button } from "./Button";

export default function ChatWindow({
  greeting,
  messages,
  onSend,
  isLoading,
}: {
  greeting: string;
  messages: ChatMessage[];
  onSend: (text: string) => void;
  isLoading: boolean;
}) {
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { t } = useTranslation();

  const submit = () => {
    const text = draft.trim();
    if (!text) return;
    onSend(text);
    setDraft("");
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-3 overflow-y-auto p-4" aria-live="polite">
        <MessageBubble message={{ role: "assistant", text: greeting }} />
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="rounded-2xl border border-[var(--line)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--ink-muted)]">
              {t("chat.thinking")}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex items-center gap-2 border-t border-[var(--line)] bg-[var(--surface)] p-3">
        <input
          ref={inputRef}
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder={t("chat.placeholder")}
          aria-label={t("chat.typeYourQuestion")}
          className="min-h-[44px] flex-1 rounded-full border border-[var(--line-strong)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--ink)]"
        />
        <VoiceButton
          onResult={(text) => {
            setDraft(text);
            // bring focus to the input once speech fills it, so pressing
            // Enter (or tapping Send) immediately after speaking just works
            inputRef.current?.focus();
          }}
        />
        <Button type="button" size="md" className="!rounded-full" onClick={submit} disabled={!draft.trim()}>
          {t("chat.send")}
        </Button>
      </div>
    </div>
  );
}
