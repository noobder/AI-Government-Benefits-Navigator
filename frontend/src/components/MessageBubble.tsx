export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

export default function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser ? "bg-brand-700 text-white" : "bg-[var(--surface)] text-[var(--ink)] border border-[var(--line)]"
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}
