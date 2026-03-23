"use client";

import { useCallback, useRef, useState } from "react";
import { Header } from "@/components/layout/Header";
import { AIText } from "@/components/ui/AIText";
import { useUserStore } from "@/stores/userStore";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Message { role: "user" | "assistant"; content: string; }

const QUICK_COMMANDS = [
  { cmd: "/market", label: "Market Overview" },
  { cmd: "/sectors", label: "Sector Rotation" },
  { cmd: "/earnings", label: "Key Earnings" },
  { cmd: "/ipo", label: "Upcoming IPOs" },
  { cmd: "/rbi", label: "RBI Policy" },
  { cmd: "/global", label: "Global Impact" },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const userType = useUserStore((s) => s.userType);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isStreaming) return;

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsStreaming(true);

    // Add empty assistant message that we'll stream into
    const assistantMsg: Message = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const response = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, user_type: userType }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              last.content += chunk;
            }
            return [...updated];
          });
          scrollToBottom();
        }
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last.role === "assistant") {
          last.content = "Failed to get response. Make sure the backend is running with a valid API key.";
        }
        return [...updated];
      });
    }

    setIsStreaming(false);
    scrollToBottom();
  }, [isStreaming, userType]);

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex flex-1 flex-col">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto max-w-2xl space-y-4">
            {messages.length === 0 && (
              <div className="py-20 text-center">
                <h2 className="mb-2 text-2xl font-bold">Ask me anything about Indian markets</h2>
                <p className="mb-8 text-sm text-[var(--text-secondary)]">
                  I&apos;m your AI financial journalist. I know Indian companies, regulations, and markets deeply.
                </p>
                {/* Quick commands */}
                <div className="flex flex-wrap justify-center gap-2">
                  {QUICK_COMMANDS.map((cmd) => (
                    <button
                      key={cmd.cmd}
                      onClick={() => sendMessage(cmd.cmd)}
                      className="rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-4 py-2 text-sm text-[var(--text-secondary)] transition-colors hover:border-[var(--accent-blue)]/50 hover:text-[var(--text-primary)]"
                    >
                      {cmd.label}
                    </button>
                  ))}
                </div>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {[
                    "Explain the Byju's crisis like I'm 19",
                    "Why is FII selling Indian stocks?",
                    "Compare TCS vs Infosys earnings",
                    "What happens if RBI cuts rates again?",
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--bg-card)] px-3 py-2 text-xs text-[var(--text-secondary)] hover:border-[var(--accent-blue)]/30"
                    >
                      &ldquo;{q}&rdquo;
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-[var(--accent-blue)] text-white"
                      : "border border-[var(--border)] bg-[var(--bg-card)]"
                  }`}
                >
                  {msg.role === "user" ? (
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                  ) : (
                    <AIText>{msg.content}</AIText>
                  )}
                  {msg.role === "assistant" && isStreaming && i === messages.length - 1 && (
                    <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse rounded-full bg-[var(--accent-salmon)]" />
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input area */}
        <div className="border-t border-[var(--border)] bg-[var(--bg-secondary)] px-4 py-3">
          <div className="mx-auto flex max-w-2xl gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
              placeholder="Ask about markets, companies, earnings, policy..."
              disabled={isStreaming}
              className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--bg-primary)] px-4 py-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:border-[var(--accent-blue)] focus:outline-none disabled:opacity-50"
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={isStreaming || !input.trim()}
              className="rounded-xl bg-[var(--accent-blue)] px-5 py-3 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
