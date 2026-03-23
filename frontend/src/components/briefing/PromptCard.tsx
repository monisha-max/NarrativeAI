"use client";

interface Props {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export function PromptCard({ label, onClick, disabled }: Props) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] px-3 py-2 text-left text-sm text-[var(--text-primary)] transition-colors hover:border-[var(--accent-blue)]/50 hover:bg-[var(--bg-secondary)] disabled:opacity-50"
    >
      {label}
    </button>
  );
}
