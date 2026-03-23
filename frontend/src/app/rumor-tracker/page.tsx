"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { AIText } from "@/components/ui/AIText";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  confirmed: { bg: "bg-green-500/10", text: "text-green-400", label: "CONFIRMED" },
  debunked: { bg: "bg-red-500/10", text: "text-red-400", label: "DEBUNKED" },
  partially_true: { bg: "bg-yellow-500/10", text: "text-yellow-400", label: "PARTIALLY TRUE" },
  unresolved: { bg: "bg-blue-500/10", text: "text-blue-400", label: "UNRESOLVED" },
};

export default function RumorTrackerPage() {
  const [rumors, setRumors] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [customRumor, setCustomRumor] = useState("");
  const [analysis, setAnalysis] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    axios.get(`${API}/rumors/all`).then((r) => {
      setRumors(r.data.rumors);
      setStats(r.data.stats);
    });
  }, []);

  const analyzeRumor = async () => {
    if (!customRumor.trim()) return;
    setAnalyzing(true);
    setAnalysis("");
    const r = await axios.post(`${API}/rumors/analyze`, null, { params: { rumor_text: customRumor } });
    setAnalysis(r.data.analysis);
    setAnalyzing(false);
  };

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-4xl px-4 py-6">
        <h1 className="mb-2 text-2xl font-bold">Rumor vs Reality</h1>
        <p className="mb-6 text-sm text-[var(--text-secondary)]">
          Tracking market rumors from whisper to outcome. No other Indian news platform does this.
        </p>

        {/* Stats */}
        {stats && (
          <div className="mb-6 grid grid-cols-4 gap-3">
            {Object.entries(STATUS_STYLES).map(([status, style]) => (
              <div key={status} className={`rounded-lg ${style.bg} p-3 text-center`}>
                <p className={`text-2xl font-bold ${style.text}`}>{stats[status] || 0}</p>
                <p className={`text-xs ${style.text}`}>{style.label}</p>
              </div>
            ))}
          </div>
        )}

        {/* Analyze your own rumor */}
        <div className="mb-6 rounded-xl border border-[var(--accent-purple)]/30 bg-[var(--accent-purple)]/5 p-6">
          <h2 className="mb-2 font-semibold text-[var(--accent-purple)]">Heard a rumor? Let AI analyze it.</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={customRumor}
              onChange={(e) => setCustomRumor(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && analyzeRumor()}
              placeholder="e.g., 'Paytm to receive banking license from RBI'"
              className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] px-4 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:border-[var(--accent-purple)] focus:outline-none"
            />
            <button
              onClick={analyzeRumor}
              disabled={analyzing}
              className="rounded-lg bg-[var(--accent-purple)] px-4 py-2 text-sm font-medium text-white hover:bg-purple-600 disabled:opacity-50"
            >
              {analyzing ? "Analyzing..." : "Analyze"}
            </button>
          </div>
          {analysis && (
            <div className="mt-4"><AIText>{analysis}</AIText></div>
          )}
        </div>

        {/* Rumor list */}
        <div className="space-y-3">
          {rumors.map((rumor) => {
            const style = STATUS_STYLES[rumor.status] || STATUS_STYLES.unresolved;
            return (
              <div key={rumor.id} className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className={`rounded-full ${style.bg} px-2 py-0.5 text-xs font-bold ${style.text}`}>
                        {style.label}
                      </span>
                      <span className="rounded-full bg-[var(--bg-secondary)] px-2 py-0.5 text-xs text-[var(--text-secondary)]">
                        {rumor.category}
                      </span>
                    </div>
                    <h3 className="mt-2 font-medium">{rumor.rumor}</h3>
                    <p className="mt-1 text-sm text-[var(--text-secondary)]">
                      Source: {rumor.source} · Surfaced: {rumor.date_surfaced}
                    </p>
                  </div>
                  {rumor.accuracy_score !== null && (
                    <div className="text-right">
                      <p className="text-xs text-[var(--text-secondary)]">Accuracy</p>
                      <p className={`text-lg font-bold ${rumor.accuracy_score >= 0.7 ? "text-green-400" : rumor.accuracy_score >= 0.4 ? "text-yellow-400" : "text-red-400"}`}>
                        {Math.round(rumor.accuracy_score * 100)}%
                      </p>
                    </div>
                  )}
                </div>
                {rumor.reality && (
                  <div className="mt-3 rounded border border-[var(--border)] bg-[var(--bg-secondary)] p-3">
                    <p className="text-xs font-medium uppercase text-[var(--text-secondary)]">Reality</p>
                    <p className="mt-1 text-sm">{rumor.reality}</p>
                    {rumor.market_impact && (
                      <p className="mt-1 text-xs text-[var(--text-secondary)]">Market impact: {rumor.market_impact}</p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
