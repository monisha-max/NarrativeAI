"use client";

interface Props {
  dossierTitle: string;
  daysSilent: number;
  severity: "medium" | "high";
  lastEventDate: string;
}

export function SilenceAlert({ dossierTitle, daysSilent, severity, lastEventDate }: Props) {
  return (
    <div className="silence-card rounded-lg bg-[var(--bg-card)] p-4">
      <div className="flex items-center gap-2">
        <span className="text-[var(--accent-amber)]">&#128263;</span>
        <span className="text-xs font-medium uppercase text-[var(--accent-amber)]">
          Silence Alert — {severity}
        </span>
      </div>
      <h3 className="mt-2 font-medium text-[var(--text-primary)]">{dossierTitle}</h3>
      <p className="mt-1 text-sm text-[var(--text-secondary)]">
        No new developments for <strong>{daysSilent} days</strong>. Last activity:{" "}
        {new Date(lastEventDate).toLocaleDateString("en-IN")}. In similar story patterns,
        prolonged silence often precedes significant developments.
      </p>
    </div>
  );
}
