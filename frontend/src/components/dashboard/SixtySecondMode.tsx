"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useUserStore } from "@/stores/userStore";

interface SixtySummary {
  most_important_change: string;
  biggest_risk: string;
  actionable_insight: string;
}

export function SixtySecondMode() {
  const userId = useUserStore((s) => s.username);
  const [summary, setSummary] = useState<SixtySummary | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    api
      .getAllDeltas(userId)
      .then((data) => setSummary(data.sixty_second_summary))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId]);

  const display = summary || {
    most_important_change: "Follow stories to get personalized change alerts.",
    biggest_risk: "Add dossiers to your watchlist to see risk analysis.",
    actionable_insight: "Search for a business story to create your first living dossier.",
  };

  return (
    <div className="relative overflow-hidden rounded-2xl border border-[var(--accent-salmon)]/20 bg-gradient-to-br from-[var(--accent-salmon)]/[0.06] via-[var(--bg-card)] to-[var(--bg-card)]">
      {/* Decorative corner accent */}
      <div className="absolute right-0 top-0 h-32 w-32 rounded-bl-full bg-gradient-to-bl from-[var(--accent-salmon)]/[0.08] to-transparent" />

      <div className="relative p-6">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent-salmon)]/10">
            <span className="text-sm">⚡</span>
          </div>
          <div>
            <h2 className="serif text-base font-bold">60-Second Briefing</h2>
            <p className="text-[10px] tracking-widest text-[var(--accent-salmon)]">AI-POWERED DAILY INTELLIGENCE</p>
          </div>
          {loading && (
            <span className="ml-auto h-3 w-3 animate-spin rounded-full border border-[var(--accent-salmon)] border-t-transparent" />
          )}
        </div>

        <div className="stagger-in grid grid-cols-1 gap-3 md:grid-cols-3">
          <div className="rounded-xl border border-[var(--market-up)]/10 bg-[var(--market-up)]/[0.03] p-4">
            <div className="mb-2 flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-[var(--market-up)]" />
              <p className="text-[10px] font-semibold tracking-widest text-[var(--market-up)]">
                MOST IMPORTANT CHANGE
              </p>
            </div>
            <p className="text-sm leading-relaxed text-[var(--text-primary)]">
              {display.most_important_change}
            </p>
          </div>
          <div className="rounded-xl border border-[var(--market-down)]/10 bg-[var(--market-down)]/[0.03] p-4">
            <div className="mb-2 flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-[var(--market-down)]" />
              <p className="text-[10px] font-semibold tracking-widest text-[var(--market-down)]">
                BIGGEST RISK
              </p>
            </div>
            <p className="text-sm leading-relaxed text-[var(--text-primary)]">
              {display.biggest_risk}
            </p>
          </div>
          <div className="rounded-xl border border-[var(--accent-blue)]/10 bg-[var(--accent-blue)]/[0.03] p-4">
            <div className="mb-2 flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-[var(--accent-blue)]" />
              <p className="text-[10px] font-semibold tracking-widest text-[var(--accent-blue)]">
                ACTIONABLE INSIGHT
              </p>
            </div>
            <p className="text-sm leading-relaxed text-[var(--text-primary)]">
              {display.actionable_insight}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
