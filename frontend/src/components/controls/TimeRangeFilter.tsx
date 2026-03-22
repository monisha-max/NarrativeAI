"use client";

import { useState } from "react";

const RANGES = ["1W", "1M", "3M", "6M", "1Y", "All"];

interface Props {
  onChange: (range: string) => void;
}

export function TimeRangeFilter({ onChange }: Props) {
  const [active, setActive] = useState("All");

  return (
    <div className="flex gap-1">
      {RANGES.map((range) => (
        <button
          key={range}
          onClick={() => {
            setActive(range);
            onChange(range);
          }}
          className={`rounded px-2 py-1 text-xs transition-colors ${
            active === range
              ? "bg-[var(--accent-blue)] text-white"
              : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--border)]"
          }`}
        >
          {range}
        </button>
      ))}
    </div>
  );
}
