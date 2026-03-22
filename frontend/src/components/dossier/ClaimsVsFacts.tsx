"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Claim {
  claim: string;
  status: string;
  detail: string;
  source: string;
  date: string;
}

interface Props {
  dossierSlug: string;
}

const STATUS_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  confirmed: { bg: "bg-[var(--market-up)]/10", text: "text-[var(--market-up)]", label: "CONFIRMED" },
  invalidated: { bg: "bg-[var(--market-down)]/10", text: "text-[var(--market-down)]", label: "INVALIDATED" },
  unverified: { bg: "bg-[var(--accent-amber)]/10", text: "text-[var(--accent-amber)]", label: "UNVERIFIED" },
  partially_confirmed: { bg: "bg-[var(--accent-blue)]/10", text: "text-[var(--accent-blue)]", label: "PARTIAL" },
};

export function ClaimsVsFacts({ dossierSlug }: Props) {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .getClaims(dossierSlug)
      .then((data) => setClaims(data.claims || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [dossierSlug]);

  if (loading) {
    return (
      <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-4">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)]">
          <div className="h-3 w-3 rounded-full bg-[var(--accent-salmon)]" />
          Claims vs. Facts
        </h3>
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 shimmer rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-4">
      <h3 className="mb-3 flex items-center gap-2 text-sm font-medium text-[var(--text-secondary)]">
        <div className="h-3 w-3 rounded-full bg-[var(--accent-salmon)]" />
        Claims vs. Facts
      </h3>

      {claims.length === 0 ? (
        <p className="py-4 text-center text-sm text-[var(--text-muted)]">
          No claims tracked yet. Build the dossier to extract claims.
        </p>
      ) : (
        <div className="space-y-2.5">
          {claims.map((item, i) => {
            const config = STATUS_CONFIG[item.status] || STATUS_CONFIG.unverified;
            return (
              <div key={i} className="rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] p-3">
                <div className="flex items-start justify-between gap-2">
                  <p className="flex-1 text-sm text-[var(--text-primary)]">{item.claim}</p>
                  <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold tracking-wider ${config.bg} ${config.text}`}>
                    {config.label}
                  </span>
                </div>
                <p className="mt-1.5 text-xs text-[var(--text-muted)]">{item.detail}</p>
                <div className="mt-1.5 flex items-center gap-3 text-[10px] text-[var(--text-muted)]">
                  {item.source && <span>Source: {item.source}</span>}
                  {item.date && <span>{item.date}</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
