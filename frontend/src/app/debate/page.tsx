"use client";

import { useState } from "react";
import { Header } from "@/components/layout/Header";
import { AIText } from "@/components/ui/AIText";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface DebateRound { round: number; bull: string; bear: string; }

export default function DebatePage() {
  const [topic, setTopic] = useState("");
  const [rounds, setRounds] = useState<DebateRound[]>([]);
  const [verdict, setVerdict] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentRound, setCurrentRound] = useState(0);

  const startDebate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setRounds([]);
    setVerdict("");
    setCurrentRound(0);

    const r = await axios.post(`${API}/debate/start`, null, { params: { topic, rounds: 3 } });

    // Reveal rounds one by one with delay for dramatic effect
    for (let i = 0; i < r.data.rounds.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setRounds((prev) => [...prev, r.data.rounds[i]]);
      setCurrentRound(i + 1);
    }

    await new Promise((resolve) => setTimeout(resolve, 800));
    setVerdict(r.data.verdict);
    setLoading(false);
  };

  const suggestions = [
    "Is Reliance overvalued at ₹2500?",
    "Will IT sector recover in FY27?",
    "Should you invest in Adani stocks now?",
    "Is the Indian real estate market in a bubble?",
    "Will RBI cut rates again in April?",
    "Is Zomato a good long-term bet?",
  ];

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-3xl px-4 py-6">
        <h1 className="mb-2 text-2xl font-bold">News Debate Arena</h1>
        <p className="mb-6 text-sm text-[var(--text-secondary)]">
          AI Bull vs Bear — 3-round live debate on any market topic. Both sides use real data.
        </p>

        {/* Topic input */}
        <div className="mb-4 flex gap-2">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !loading && startDebate()}
            placeholder="Enter any market topic or question..."
            className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] px-4 py-3 text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:border-[var(--accent-blue)] focus:outline-none"
          />
          <button
            onClick={startDebate}
            disabled={loading || !topic.trim()}
            className="rounded-lg bg-[var(--accent-blue)] px-6 py-3 font-medium text-white hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? "Debating..." : "Start Debate"}
          </button>
        </div>

        {/* Suggestions */}
        {rounds.length === 0 && (
          <div className="mb-8 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => { setTopic(s); }}
                className="rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1.5 text-xs text-[var(--text-secondary)] hover:border-[var(--accent-blue)]/50"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Debate rounds */}
        <div className="space-y-6">
          {rounds.map((round) => (
            <div key={round.round} className="animate-in fade-in">
              <p className="mb-3 text-center text-xs font-medium uppercase text-[var(--text-secondary)]">
                Round {round.round}
              </p>
              <div className="grid grid-cols-2 gap-3">
                {/* Bull */}
                <div className="rounded-lg border border-green-500/30 bg-green-500/5 p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <span className="text-lg">&#128002;</span>
                    <span className="text-xs font-bold uppercase text-green-400">Bull</span>
                  </div>
                  <AIText>{round.bull}</AIText>
                </div>
                {/* Bear */}
                <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <span className="text-lg">&#128059;</span>
                    <span className="text-xs font-bold uppercase text-red-400">Bear</span>
                  </div>
                  <AIText>{round.bear}</AIText>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Verdict */}
        {verdict && (
          <div className="mt-6 rounded-xl border border-[var(--accent-amber)]/30 bg-[var(--accent-amber)]/5 p-6">
            <div className="mb-2 flex items-center gap-2">
              <span className="text-lg">&#9878;&#65039;</span>
              <h3 className="font-bold text-[var(--accent-amber)]">VERDICT</h3>
            </div>
            <AIText>{verdict}</AIText>
          </div>
        )}

        {/* Loading indicator */}
        {loading && rounds.length > 0 && (
          <div className="mt-4 text-center">
            <div className="inline-flex items-center gap-2 rounded-full bg-[var(--bg-card)] px-4 py-2">
              <div className="h-3 w-3 animate-spin rounded-full border border-[var(--accent-blue)] border-t-transparent" />
              <span className="text-xs text-[var(--text-secondary)]">
                {currentRound < 3 ? `Round ${currentRound + 1} in progress...` : "Judge deliberating..."}
              </span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
