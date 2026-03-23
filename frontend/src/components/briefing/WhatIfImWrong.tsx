"use client";

import { useStreamingResponse } from "@/hooks/useStreamingResponse";
import { StreamingResponse } from "./StreamingResponse";

interface Props {
  dossierSlug: string;
}

export function WhatIfImWrong({ dossierSlug }: Props) {
  const { text, isStreaming, stream, reset } = useStreamingResponse();

  const handleClick = () => {
    reset();
    stream(dossierSlug, { prompt_key: "what_if_wrong" });
  };

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={isStreaming}
        className="w-full rounded-md border border-[var(--accent-purple)]/30 bg-[var(--accent-purple)]/10 py-3 text-sm font-medium text-[var(--accent-purple)] transition-colors hover:bg-[var(--accent-purple)]/20 disabled:opacity-50"
      >
        What if I&apos;m wrong?
      </button>
      {(text || isStreaming) && (
        <div className="mt-4">
          <StreamingResponse text={text} isStreaming={isStreaming} />
        </div>
      )}
    </div>
  );
}
