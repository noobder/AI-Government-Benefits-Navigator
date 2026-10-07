import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ChatWindow from "../components/ChatWindow";
import type { ChatMessage } from "../components/MessageBubble";
import SchemeCard from "../components/SchemeCard";
import EmptyState from "../components/EmptyState";
import { useAppState } from "../hooks/useAppState";
import { useVoice } from "../hooks/useVoice";
import { chatApi } from "../services/chat";
import type { RecommendedScheme } from "../types/scheme";

export default function Chat() {
  const { language, userId, profile, setProfile } = useAppState();
  const { speak, isSynthesisSupported } = useVoice(language);
  const { t } = useTranslation();
  const location = useLocation() as { state?: { initialMessage?: string } };

  // The greeting is rendered live from the current language rather than
  // frozen into message state, so switching languages mid-conversation
  // still shows a correctly translated greeting.
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendedScheme[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sentInitial = useRef(false);

  const knownProfileRef = useRef<Record<string, unknown>>({});

  const sendMessage = async (text: string) => {
    setMessages((m) => [...m, { role: "user", text }]);
    setIsLoading(true);
    setError(null);
    try {
      const resp = await chatApi.send(text, language, knownProfileRef.current, userId ?? undefined);
      knownProfileRef.current = resp.extracted_profile;
      setProfile({ ...profile, ...resp.extracted_profile });

      let replyText = resp.reply_text;
      if (resp.follow_up_question) {
        replyText += `\n\n${resp.follow_up_question}`;
      }
      setMessages((m) => [...m, { role: "assistant", text: replyText }]);
      setRecommendations(resp.recommendations);
      if (isSynthesisSupported) speak(replyText);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.genericError"));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (location.state?.initialMessage && !sentInitial.current) {
      sentInitial.current = true;
      sendMessage(location.state.initialMessage);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  return (
    <div className="mx-auto grid max-w-6xl grid-cols-1 gap-4 px-4 py-6 md:grid-cols-2">
      <div className="flex h-[70vh] flex-col overflow-hidden rounded-2xl border border-[var(--line)] bg-[var(--surface-2)] md:h-[75vh]">
        <ChatWindow greeting={t("chat.welcome")} messages={messages} onSend={sendMessage} isLoading={isLoading} />
      </div>

      <div className="max-h-[70vh] space-y-4 overflow-y-auto md:max-h-[75vh]">
        {error && <p className="rounded-xl bg-[var(--danger-weak)] p-3 text-sm text-[var(--danger)]">{error}</p>}
        {recommendations.length === 0 && !isLoading && (
          <EmptyState title={t("chat.noRecommendationsTitle")} description={t("chat.noRecommendationsDesc")} />
        )}
        {recommendations.map((r) => (
          <SchemeCard key={r.scheme.scheme_id} item={r} />
        ))}
      </div>
    </div>
  );
}
