"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useStreamingResponse } from "@/hooks/useStreamingResponse";
import { StreamingResponse } from "@/components/briefing/StreamingResponse";

interface ContrarianData {
  consensus: { summary: string; key_evidence: string[]; confidence: number };
  contrarian_view: { summary: string; key_evidence: string[]; confidence: number };
  evidence_comparison: { point: string; supports: string; strength: string }[];
  unresolved_questions: string[];
  verdict: string;
}

interface Props {
  dossierSlug: string;
}

export function ContrarianPanel({ dossierSlug }: Props) {
  const [data, setData] = useState<ContrarianData | null>(null);
  const [loading, setLoading] = useState(true);
  const { text: wrongText, isStreaming, stream, reset } = useStreamingResponse();

  useEffect(() => {
    setLoading(true);
    api
      .getContrarian(dossierSlug)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [dossierSlug]);

  const handleWhatIfWrong = () => {
    reset();
    stream(dossierSlug, { prompt_key: "what_if_wrong" });
  };

  if (loading) {
    return (
      <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-5">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)]">
          <div className="h-3 w-3 rounded-full bg-[var(--accent-salmon)]" />
          Consensus vs. Contrarian
        </h3>
        <div className="space-y-3">
          <div className="h-20 shimmer rounded-lg" />
          <div className="h-20 shimmer rounded-lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-5">
      <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)]">
        <div className="h-3 w-3 rounded-full bg-[var(--accent-salmon)]" />
        Consensus vs. Contrarian
      </h3>

      {data ? (
        <>
          <div className="grid grid-cols-2 gap-4">
            {/* Consensus */}
            <div className="rounded-lg border border-[var(--market-up)]/20 bg-[var(--market-up)]/[0.03] p-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-[10px] font-semibold tracking-widest text-[var(--market-up)]">CONSENSUS</p>
                <span className="mono text-xs text-[var(--market-up)]">
                  {Math.round((data.consensus?.confidence || 0) * 100)}%
                </span>
              </div>
              <p className="text-sm leading-relaxed">{data.consensus?.summary}</p>
              {data.consensus?.key_evidence?.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {data.consensus.key_evidence.slice(0, 3).map((e, i) => (
                    <li key={i} className="text-xs text-[var(--text-muted)]">• {e}</li>
                  ))}
                </ul>
              )}
            </div>

            {/* Contrarian */}
            <div className="rounded-lg border border-[var(--market-down)]/20 bg-[var(--market-down)]/[0.03] p-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-[10px] font-semibold tracking-widest text-[var(--market-down)]">CONTRARIAN</p>
                <span className="mono text-xs text-[var(--market-down)]">
                  {Math.round((data.contrarian_view?.confidence || 0) * 100)}%
                </span>
              </div>
              <p className="text-sm leading-relaxed">{data.contrarian_view?.summary || "No credible contrarian view found."}</p>
              {data.contrarian_view?.key_evidence?.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {data.contrarian_view.key_evidence.slice(0, 3).map((e, i) => (
                    <li key={i} className="text-xs text-[var(--text-muted)]">• {e}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Unresolved questions */}
          {data.unresolved_questions?.length > 0 && (
            <div className="mt-4">
              <p className="text-[10px] font-semibold tracking-widest text-[var(--accent-amber)]">UNRESOLVED QUESTIONS</p>
              <ul className="mt-1 space-y-1">
                {data.unresolved_questions.slice(0, 3).map((q, i) => (
                  <li key={i} className="text-xs text-[var(--text-secondary)]">? {q}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      ) : (
        <p className="py-4 text-center text-sm text-[var(--text-muted)]">
          Contrarian analysis unavailable. Ensure your API key is configured.
        </p>
      )}

      {/* What If I'm Wrong */}
      <button
        onClick={handleWhatIfWrong}
        disabled={isStreaming}
        className="mt-4 w-full rounded-lg border border-[var(--accent-purple)]/20 bg-[var(--accent-purple)]/[0.05] py-2.5 text-sm font-medium text-[var(--accent-purple)] transition-all hover:bg-[var(--accent-purple)]/10 disabled:opacity-50"
      >
        {isStreaming ? "Thinking..." : "What if I'm wrong?"}
      </button>

      {(wrongText || isStreaming) && (
        <div className="mt-3">
          <StreamingResponse text={wrongText} isStreaming={isStreaming} />
        </div>
      )}
    </div>
  );
}
