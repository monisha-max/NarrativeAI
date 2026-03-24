"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { api } from "@/lib/api";
import type { Dossier } from "@/types/dossier";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Dossier[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const router = useRouter();

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      // Search existing dossiers
      const data = await api.getDossiers();
      const q = query.toLowerCase();
      const queryWords = q.split(/\s+/);
      const filtered = data.dossiers.filter((d) => {
        const title = d.title.toLowerCase();
        const desc = (d.description || "").toLowerCase();
        const tags = (d.tags || []).join(" ").toLowerCase();
        const all = `${title} ${desc} ${tags}`;
        return queryWords.some((word) => all.includes(word));
      });
      setResults(filtered);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDossier = async () => {
    if (!query.trim()) return;
    setCreating(true);
    try {
      // First check if a matching dossier already exists
      const data = await api.getDossiers();
      const match = data.dossiers.find(
        (d) => d.title.toLowerCase().includes(query.toLowerCase()) ||
               query.toLowerCase().includes(d.title.toLowerCase().replace(" cycle", ""))
      );
      if (match) {
        router.push(`/dossier/${match.slug}`);
        return;
      }
      // Otherwise create new
      const dossier = await api.createDossier(query);
      router.push(`/dossier/${dossier.slug}`);
    } catch (err) {
      console.error("Failed to create dossier:", err);
      // If create fails (e.g. duplicate slug), try to navigate by slug
      const slug = query.toLowerCase().replace(/[^\w\s-]/g, "").replace(/[\s]+/g, "-");
      router.push(`/dossier/${slug}`);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="mb-2 text-2xl font-bold text-[var(--text-primary)]">
          Search or Create a Dossier
        </h1>
        <p className="mb-8 text-sm text-[var(--text-secondary)]">
          Search for an existing story or type a new topic to create a living dossier.
        </p>

        {/* Search input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="e.g., Byju's crisis, Adani-Hindenburg, RBI rate decision..."
            className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] px-4 py-3 text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:border-[var(--accent-blue)] focus:outline-none"
          />
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="rounded-lg bg-[var(--accent-blue)] px-6 py-3 font-medium text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div className="mt-6 space-y-3">
            <h2 className="text-sm font-medium text-[var(--text-secondary)]">
              Existing Dossiers
            </h2>
            {results.map((dossier) => (
              <button
                key={dossier.id}
                onClick={() => router.push(`/dossier/${dossier.slug}`)}
                className="block w-full rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4 text-left transition-colors hover:border-[var(--accent-blue)]/50"
              >
                <h3 className="font-medium text-[var(--text-primary)]">{dossier.title}</h3>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                  {dossier.description || `${dossier.events.length} events tracked`}
                </p>
              </button>
            ))}
          </div>
        )}

        {/* Create new dossier */}
        {query.trim() && (
          <div className="mt-6">
            <div className="rounded-lg border border-dashed border-[var(--accent-blue)]/30 bg-[var(--accent-blue)]/5 p-6 text-center">
              <p className="mb-3 text-sm text-[var(--text-secondary)]">
                Don&apos;t see what you&apos;re looking for?
              </p>
              <button
                onClick={handleCreateDossier}
                disabled={creating}
                className="rounded-lg bg-[var(--accent-blue)] px-6 py-2.5 font-medium text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
              >
                {creating ? "Creating..." : `Create dossier: "${query}"`}
              </button>
              <p className="mt-2 text-xs text-[var(--text-secondary)]">
                This will create a new living dossier and begin ingesting articles about this topic.
              </p>
            </div>
          </div>
        )}

        {/* Suggested topics */}
        <div className="mt-10">
          <h2 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">
            Suggested Topics
          </h2>
          <div className="flex flex-wrap gap-2">
            {[
              "Byju's Crisis",
              "Adani-Hindenburg",
              "RBI Rate Decision",
              "Union Budget 2026",
              "Paytm-RBI",
              "India EV Policy",
              "HDFC Bank Merger",
              "Zee-Sony Deal",
            ].map((topic) => (
              <button
                key={topic}
                onClick={() => {
                  setQuery(topic);
                  handleSearch();
                }}
                className="rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1.5 text-sm text-[var(--text-secondary)] transition-colors hover:border-[var(--accent-blue)]/50 hover:text-[var(--text-primary)]"
              >
                {topic}
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
