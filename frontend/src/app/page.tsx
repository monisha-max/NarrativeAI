"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { SixtySecondMode } from "@/components/dashboard/SixtySecondMode";
import { DeltaCardList } from "@/components/dashboard/DeltaCardList";
import { TrendingStories } from "@/components/dashboard/TrendingStories";
import { api } from "@/lib/api";
import type { Dossier } from "@/types/dossier";

const FEATURE_CARDS = [
  {
    href: "/market-pulse",
    title: "Market Pulse Live",
    description: "Real-time indices, sector heatmap, AI commentary",
    icon: "&#128200;",
    color: "var(--accent-green)",
  },
  {
    href: "/chat",
    title: "AI Chat",
    description: "Ask anything about Indian markets",
    icon: "&#128172;",
    color: "var(--accent-blue)",
  },
  {
    href: "/debate",
    title: "Debate Arena",
    description: "AI Bull vs Bear live debate on any topic",
    icon: "&#9878;&#65039;",
    color: "var(--accent-amber)",
  },
  {
    href: "/earnings",
    title: "Earnings Decoder",
    description: "AI decodes quarterly results instantly",
    icon: "&#128202;",
    color: "var(--accent-purple)",
  },
  {
    href: "/rumor-tracker",
    title: "Rumor vs Reality",
    description: "Track market rumors from whisper to outcome",
    icon: "&#128269;",
    color: "var(--accent-red)",
  },
  {
    href: "/portfolio-impact",
    title: "Portfolio Simulator",
    description: "How does this news affect YOUR portfolio?",
    icon: "&#128176;",
    color: "var(--accent-orange)",
  },
];

export default function HomePage() {
  const [dossiers, setDossiers] = useState<Dossier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getDossiers();
        setDossiers(data.dossiers);
      } catch (err) {
        console.error("Failed to load dossiers:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-7xl px-4 py-6">
        {/* 60-Second Mode */}
        <section className="mb-8">
          <SixtySecondMode />
        </section>

        {/* Feature Cards */}
        <section className="mb-8">
          <div className="mb-4 flex items-center gap-3">
            <div className="h-4 w-0.5 rounded-full bg-[var(--accent-salmon)]" />
            <h2 className="serif text-lg font-semibold text-[var(--text-primary)]">
              Intelligence Tools
            </h2>
          </div>
          <div className="stagger-in grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {FEATURE_CARDS.map((card) => (
              <Link
                key={card.href}
                href={card.href}
                className="card-glow group rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-4 transition-all"
              >
                <span className="text-2xl" dangerouslySetInnerHTML={{ __html: card.icon }} />
                <h3 className="mt-2 text-sm font-medium text-[var(--text-primary)] group-hover:text-[var(--accent-salmon)]">
                  {card.title}
                </h3>
                <p className="mt-1 text-[11px] leading-relaxed text-[var(--text-muted)]">{card.description}</p>
              </Link>
            ))}
          </div>
        </section>

        {/* Living Dossiers */}
        <section className="mb-8">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-4 w-0.5 rounded-full bg-[var(--accent-salmon)]" />
              <h2 className="serif text-lg font-semibold text-[var(--text-primary)]">
                Living Dossiers
              </h2>
            </div>
            <Link
              href="/search"
              className="rounded-full border border-[var(--accent-salmon)]/20 bg-[var(--accent-salmon)]/5 px-3 py-1 text-xs font-medium text-[var(--accent-salmon)] hover:bg-[var(--accent-salmon)]/10"
            >
              + New Dossier
            </Link>
          </div>
          {loading ? (
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 rounded-lg bg-[var(--bg-card)]" />
              ))}
            </div>
          ) : (
            <DeltaCardList dossiers={dossiers} />
          )}
        </section>

        {/* Trending */}
        <section>
          <h2 className="mb-4 text-lg font-semibold text-[var(--text-secondary)]">
            Trending Story Arcs
          </h2>
          <TrendingStories dossiers={dossiers} />
        </section>
      </main>
    </div>
  );
}
