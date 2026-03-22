"use client";

import type { RippleAlert } from "@/types/ripple";

interface Props {
  alerts: RippleAlert[];
}

export function RippleIndicators({ alerts }: Props) {
  if (alerts.length === 0) return null;

  return (
    <div className="space-y-2">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="rounded border border-[var(--accent-purple)]/20 bg-[var(--accent-purple)]/5 p-2"
        >
          <p className="text-xs text-[var(--accent-purple)]">
            Cross-story ripple detected (magnitude: {Math.round(alert.magnitude * 100)}%)
          </p>
          <p className="mt-1 text-xs text-[var(--text-secondary)]">
            {alert.impact_description}
          </p>
        </div>
      ))}
    </div>
  );
}
