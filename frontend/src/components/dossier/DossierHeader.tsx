"use client";

import Link from "next/link";
import type { Dossier } from "@/types/dossier";
import { VELOCITY_COLORS, VELOCITY_LABELS } from "@/lib/constants";
import { LanguageSwitcher } from "@/components/controls/LanguageSwitcher";

interface Props {
  dossier: Dossier;
}

export function DossierHeader({ dossier }: Props) {
  return (
    <div className="border-b border-[var(--border)] bg-[var(--bg-secondary)] px-4 py-3">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div>
          <h1 className="serif text-xl font-bold text-[var(--text-primary)]">{dossier.title}</h1>
          <div className="mt-1 flex items-center gap-3 text-sm">
            <span
              className="rounded-full px-2 py-0.5 text-xs font-medium"
              style={{
                color: VELOCITY_COLORS[dossier.velocity],
                backgroundColor: `${VELOCITY_COLORS[dossier.velocity]}20`,
              }}
            >
              {VELOCITY_LABELS[dossier.velocity]}
            </span>
            <span className="text-[var(--text-secondary)]">
              {dossier.article_count} articles · {dossier.events.length} events
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <LanguageSwitcher />
          <Link
            href={`/briefing/${dossier.slug}`}
            className="rounded-lg bg-[var(--accent-salmon)] px-4 py-2 text-sm font-medium text-[var(--et-navy)] transition-all hover:shadow-lg hover:shadow-[var(--accent-salmon)]/10"
          >
            Briefing Room
          </Link>
        </div>
      </div>
    </div>
  );
}
