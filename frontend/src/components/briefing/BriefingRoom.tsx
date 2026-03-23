"use client";

import { useState } from "react";
import { PromptCard } from "./PromptCard";
import { StreamingResponse } from "./StreamingResponse";
import { useStreamingResponse } from "@/hooks/useStreamingResponse";
import { useUserStore } from "@/stores/userStore";
import { LanguageSwitcher } from "@/components/controls/LanguageSwitcher";
import { api } from "@/lib/api";

const GUIDED_PROMPTS = [
  { key: "explain", label: "Explain the story" },
  { key: "what_changed", label: "What changed today?" },
  { key: "who_exposed", label: "Who is exposed?" },
  { key: "opposing_takes", label: "Give me opposing takes" },
  { key: "eli19", label: "Explain like I'm 19" },
  { key: "what_if_wrong", label: "What if I'm wrong?" },
  { key: "portfolio_relevant", label: "Relevant to my portfolio" },
  { key: "story_dna", label: "What's the story's DNA?" },
  { key: "sixty_second", label: "60-second version" },
];

interface Props {
  dossierSlug: string;
}

export function BriefingRoom({ dossierSlug }: Props) {
  const [customQuery, setCustomQuery] = useState("");
  const { text, isStreaming, stream, reset } = useStreamingResponse();
  const [translatedText, setTranslatedText] = useState("");
  const [translating, setTranslating] = useState(false);
  const userType = useUserStore((s) => s.userType);
  const language = useUserStore((s) => s.language);

  const handlePrompt = (promptKey: string) => {
    reset();
    setTranslatedText("");
    stream(dossierSlug, { prompt_key: promptKey, user_type: userType, language });
  };

  const handleCustom = () => {
    if (!customQuery.trim()) return;
    reset();
    setTranslatedText("");
    stream(dossierSlug, { custom_query: customQuery, user_type: userType, language });
  };

  const handleTranslate = async () => {
    if (!text || language === "en") return;
    setTranslating(true);
    try {
      const result = await api.translate(text, language, userType);
      setTranslatedText(result.translated);
    } catch {
      setTranslatedText("Translation failed. Check API key.");
    }
    setTranslating(false);
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="h-5 w-0.5 rounded-full bg-[var(--accent-salmon)]" />
            <h2 className="serif text-xl font-bold text-[var(--text-primary)]">Briefing Room</h2>
          </div>
          <p className="mt-1 ml-5 text-sm text-[var(--text-muted)]">
            Ask anything about this story. Adapted to your profile ({userType.replace("_", " ")}).
          </p>
        </div>
        <LanguageSwitcher />
      </div>

      {/* Guided prompts */}
      <div className="mb-6 grid grid-cols-3 gap-2 sm:grid-cols-3 lg:grid-cols-5">
        {GUIDED_PROMPTS.map((prompt) => (
          <PromptCard
            key={prompt.key}
            label={prompt.label}
            onClick={() => handlePrompt(prompt.key)}
            disabled={isStreaming}
          />
        ))}
      </div>

      {/* Custom query */}
      <div className="mb-6 flex gap-2">
        <input
          type="text"
          value={customQuery}
          onChange={(e) => setCustomQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCustom()}
          placeholder="Ask anything about this story..."
          className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--bg-secondary)] px-4 py-2.5 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent-salmon)] focus:outline-none"
        />
        <button
          onClick={handleCustom}
          disabled={isStreaming || !customQuery.trim()}
          className="rounded-xl bg-[var(--accent-salmon)] px-5 py-2.5 text-sm font-medium text-[var(--et-navy)] transition-all hover:shadow-lg hover:shadow-[var(--accent-salmon)]/10 disabled:opacity-50"
        >
          Ask
        </button>
      </div>

      {/* Response */}
      {(text || isStreaming) && (
        <div className="space-y-3">
          <StreamingResponse text={text} isStreaming={isStreaming} />

          {/* Translate button — shows when language isn't English and response is complete */}
          {text && !isStreaming && language !== "en" && !translatedText && (
            <button
              onClick={handleTranslate}
              disabled={translating}
              className="rounded-lg border border-[var(--accent-salmon)]/20 bg-[var(--accent-salmon)]/[0.05] px-4 py-2 text-xs font-medium text-[var(--accent-salmon)] transition-all hover:bg-[var(--accent-salmon)]/10 disabled:opacity-50"
            >
              {translating ? "Translating..." : `Translate to ${language === "hi" ? "Hindi" : language === "te" ? "Telugu" : language === "ta" ? "Tamil" : language === "bn" ? "Bengali" : language}`}
            </button>
          )}

          {/* Translated response */}
          {translatedText && (
            <div className="rounded-xl border border-[var(--accent-salmon)]/20 bg-[var(--accent-salmon)]/[0.03] p-6">
              <p className="mb-2 text-[10px] font-semibold tracking-widest text-[var(--accent-salmon)]">
                VERNACULAR TRANSLATION
              </p>
              <div className="whitespace-pre-line text-sm leading-relaxed">
                {translatedText}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
