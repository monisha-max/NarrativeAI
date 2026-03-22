"use client";

import { VELOCITY_COLORS, VELOCITY_LABELS } from "@/lib/constants";

interface Props {
  velocity: string;
}

export function NarrativeVelocity({ velocity }: Props) {
  const color = VELOCITY_COLORS[velocity] || "#6B7280";
  const label = VELOCITY_LABELS[velocity] || velocity;

  return (
    <div className="flex items-center gap-2">
      <div
        className="h-2 w-2 rounded-full"
        style={{ backgroundColor: color }}
      />
      <span className="text-xs font-medium" style={{ color }}>
        {label}
      </span>
    </div>
  );
}
