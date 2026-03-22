"use client";

import Link from "next/link";
import type { Dossier } from "@/types/dossier";

interface Props {
  dossiers: Dossier[];
}

export function TrendingStories({ dossiers }: Props) {
  if (dossiers.length === 0) {
    return (
      <p className="text-sm text-[var(--text-secondary)]">
        No trending stories available yet.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {dossiers.slice(0, 6).map((dossier) => (
        <Link
          key={dossier.id}
          href={`/dossier/${dossier.slug}`}
          className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4 transition-colors hover:border-[var(--accent-blue)]/50"
        >
          <h3 className="text-sm font-medium text-[var(--text-primary)]">{dossier.title}</h3>
          <div className="mt-2 flex items-center gap-2 text-xs text-[var(--text-secondary)]">
            <span>{dossier.article_count} articles</span>
            <span>·</span>
            <span>{dossier.events.length} events</span>
          </div>
          {dossier.tags && (
            <div className="mt-2 flex flex-wrap gap-1">
              {dossier.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="rounded bg-[var(--bg-secondary)] px-1.5 py-0.5 text-xs text-[var(--text-secondary)]"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </Link>
      ))}
    </div>
  );
}
