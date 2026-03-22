"use client";

import type { StoryDNA as StoryDNAType } from "@/types/archetype";

interface Props {
  dna: StoryDNAType;
}

export function StoryDNA({ dna }: Props) {
  const { archetype, current_phase, confidence, phase_prediction } = dna;

  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase text-[var(--text-secondary)]">Story DNA</p>
          <p className="mt-1 font-medium text-[var(--text-primary)]">{archetype.name}</p>
        </div>
        <span className="rounded-full bg-[var(--accent-blue)]/20 px-2 py-1 text-xs text-[var(--accent-blue)]">
          {Math.round(confidence * 100)}% match
        </span>
      </div>

      {/* Phase progression bar */}
      <div className="mt-4">
        <div className="flex gap-1">
          {archetype.phases.map((phase) => (
            <div
              key={phase.phase_number}
              className="flex-1 rounded-sm py-1 text-center text-xs"
              style={{
                backgroundColor:
                  phase.phase_number === current_phase
                    ? "var(--accent-blue)"
                    : phase.phase_number < current_phase
                      ? "var(--accent-blue)40"
                      : "var(--bg-secondary)",
                color:
                  phase.phase_number === current_phase
                    ? "#fff"
                    : "var(--text-secondary)",
              }}
            >
              {phase.phase_number}
            </div>
          ))}
        </div>
        <p className="mt-2 text-xs text-[var(--text-secondary)]">
          Phase {current_phase}: {archetype.phases.find((p) => p.phase_number === current_phase)?.name}
        </p>
      </div>

      {/* Phase prediction */}
      {phase_prediction && (
        <div className="mt-3 rounded border border-[var(--accent-amber)]/20 bg-[var(--accent-amber)]/5 p-2">
          <p className="text-xs text-[var(--accent-amber)]">
            Phase {phase_prediction.next_phase} predicted within ~{phase_prediction.estimated_days} days
            ({Math.round(phase_prediction.probability * 100)}% probability)
          </p>
        </div>
      )}
    </div>
  );
}
