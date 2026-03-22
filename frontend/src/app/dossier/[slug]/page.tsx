"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { DossierHeader } from "@/components/dossier/DossierHeader";
import { Timeline } from "@/components/dossier/Timeline";
import { EntityGraph } from "@/components/dossier/EntityGraph";
import { SentimentArc } from "@/components/dossier/SentimentArc";
import { ClaimsVsFacts } from "@/components/dossier/ClaimsVsFacts";
import { ContrarianPanel } from "@/components/dossier/ContrarianPanel";
import { StoryDNA } from "@/components/dossier/StoryDNA";
import { RippleIndicators } from "@/components/dossier/RippleIndicators";
import { PerspectiveDial } from "@/components/controls/PerspectiveDial";
import { api } from "@/lib/api";
import type { Dossier } from "@/types/dossier";
import type { StoryDNA as StoryDNAType } from "@/types/archetype";
import type { RippleAlert } from "@/types/ripple";

export default function DossierPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [dossier, setDossier] = useState<Dossier | null>(null);
  const [storyDNA, setStoryDNA] = useState<StoryDNAType | null>(null);
  const [rippleAlerts, setRippleAlerts] = useState<RippleAlert[]>([]);
  const [activePanel, setActivePanel] = useState<"graph" | "sentiment" | "claims">("graph");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [dossierData, rippleData] = await Promise.all([
          api.getDossier(slug),
          api.getRipples(slug).catch(() => ({ alerts: [] })),
        ]);
        setDossier(dossierData);
        setRippleAlerts(rippleData.alerts || []);

        // Try to load Story DNA (may not exist yet)
        try {
          const dna = await api.getStoryDNA(slug);
          setStoryDNA(dna);
        } catch {
          // DNA not computed yet — that's fine
        }
      } catch (err) {
        console.error("Failed to load dossier:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--accent-blue)] border-t-transparent" />
        </div>
      </div>
    );
  }

  if (!dossier) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="py-20 text-center text-[var(--text-secondary)]">Dossier not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      <DossierHeader dossier={dossier} />

      <main className="mx-auto max-w-7xl px-4 py-6">
        {/* Story DNA + Ripple alerts */}
        <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          {storyDNA && <StoryDNA dna={storyDNA} />}
          {rippleAlerts.length > 0 && <RippleIndicators alerts={rippleAlerts} />}
        </div>

        {/* Main content */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Main: Timeline with Fog of War */}
          <div className="lg:col-span-2">
            <Timeline events={dossier.events} />
          </div>

          {/* Sidebar: Panels */}
          <div className="space-y-4">
            <div className="flex gap-2">
              {(["graph", "sentiment", "claims"] as const).map((panel) => (
                <button
                  key={panel}
                  onClick={() => setActivePanel(panel)}
                  className={`rounded-md px-3 py-1.5 text-sm capitalize transition-colors ${
                    activePanel === panel
                      ? "bg-[var(--accent-blue)] text-white"
                      : "bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--border)]"
                  }`}
                >
                  {panel === "graph"
                    ? "Money Map"
                    : panel === "claims"
                      ? "Claims vs Facts"
                      : "Sentiment"}
                </button>
              ))}
            </div>

            {activePanel === "graph" && <EntityGraph dossierSlug={slug} />}
            {activePanel === "sentiment" && <SentimentArc events={dossier.events} />}
            {activePanel === "claims" && <ClaimsVsFacts dossierSlug={slug} />}
          </div>
        </div>

        {/* Bottom: Contrarian + Perspective */}
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ContrarianPanel dossierSlug={slug} />
          <PerspectiveDial />
        </div>

        {/* Silence alert (from Story DNA) */}
        {storyDNA?.silence_alert && (
          <div className="mt-6 silence-card rounded-lg bg-[var(--bg-card)] p-4">
            <div className="flex items-center gap-2">
              <span className="text-[var(--accent-amber)]">&#128263;</span>
              <span className="text-xs font-medium uppercase text-[var(--accent-amber)]">
                Silence Alert — {storyDNA.silence_alert.severity}
              </span>
            </div>
            <p className="mt-2 text-sm text-[var(--text-primary)]">
              No new developments for <strong>{storyDNA.silence_alert.days_silent} days</strong>.
              Expected ~{storyDNA.silence_alert.expected_events} events during this period based on
              historical cadence.
            </p>
            {(storyDNA.silence_alert as any).explanation && (
              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                {(storyDNA.silence_alert as any).explanation}
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
