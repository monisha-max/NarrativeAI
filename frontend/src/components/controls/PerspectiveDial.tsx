"use client";

import { usePerspectiveStore } from "@/stores/perspectiveStore";

export function PerspectiveDial() {
  const {
    risk, sentiment, geography, depth, stakeholder,
    setRisk, setSentiment, setGeography, setDepth, setStakeholder, reset,
  } = usePerspectiveStore();

  const sliders = [
    { label: "Conservative / Aggressive", value: risk, setter: setRisk, left: "Conservative", right: "Aggressive" },
    { label: "Bear / Bull", value: sentiment, setter: setSentiment, left: "Bear", right: "Bull" },
    { label: "India-First / Global", value: geography, setter: setGeography, left: "India-First", right: "Global" },
    { label: "Quick Take / Deep Evidence", value: depth, setter: setDepth, left: "Quick", right: "Deep" },
  ];

  const stakeholders = ["investor", "founder", "employee", "regulator"];

  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-medium text-[var(--text-secondary)]">Perspective Dial</h3>
        <button
          onClick={reset}
          className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
        >
          Reset
        </button>
      </div>

      {/* Stakeholder selector */}
      <div className="mb-4 flex gap-1">
        {stakeholders.map((s) => (
          <button
            key={s}
            onClick={() => setStakeholder(s)}
            className={`flex-1 rounded py-1 text-xs capitalize transition-colors ${
              stakeholder === s
                ? "bg-[var(--accent-blue)] text-white"
                : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--border)]"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Sliders */}
      <div className="space-y-3">
        {sliders.map((slider) => (
          <div key={slider.label}>
            <div className="flex justify-between text-xs text-[var(--text-secondary)]">
              <span>{slider.left}</span>
              <span>{slider.right}</span>
            </div>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={slider.value}
              onChange={(e) => slider.setter(parseFloat(e.target.value))}
              className="mt-1 w-full accent-[var(--accent-blue)]"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
