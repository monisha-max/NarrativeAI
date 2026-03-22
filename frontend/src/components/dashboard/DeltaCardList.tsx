"use client";

import Link from "next/link";
import type { Dossier } from "@/types/dossier";
import { VELOCITY_COLORS, VELOCITY_LABELS } from "@/lib/constants";
import { formatRelativeTime } from "@/lib/utils";

interface Props {
  dossiers: Dossier[];
}

export function DeltaCardList({ dossiers }: Props) {
  if (dossiers.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-[var(--border)] p-8 text-center text-[var(--text-secondary)]">
        No dossiers yet. Create one to start tracking a story.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {dossiers.map((dossier) => (
        <Link
          key={dossier.id}
          href={`/dossier/${dossier.slug}`}
          className="block rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4 transition-colors hover:border-[var(--accent-blue)]/50"
        >
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-medium text-[var(--text-primary)]">{dossier.title}</h3>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                {dossier.description || `${dossier.article_count} articles tracked`}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span
                className="rounded-full px-2 py-0.5 text-xs font-medium"
                style={{
                  color: VELOCITY_COLORS[dossier.velocity] || "#6B7280",
                  backgroundColor: `${VELOCITY_COLORS[dossier.velocity] || "#6B7280"}20`,
                }}
              >
                {VELOCITY_LABELS[dossier.velocity] || dossier.velocity}
              </span>
              <span className="text-xs text-[var(--text-secondary)]">
                {dossier.events.length} events
              </span>
            </div>
          </div>
          <div className="mt-2 text-xs text-[var(--text-secondary)]">
            Updated {formatRelativeTime(dossier.updated_at)}
          </div>
        </Link>
      ))}
    </div>
  );
}
