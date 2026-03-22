"use client";

interface FogSegment {
  x: number;
  width: number;
  density: number;
}

interface Props {
  segments: FogSegment[];
  height: number;
}

export function FogOfWar({ segments, height }: Props) {
  return (
    <svg className="pointer-events-none absolute inset-0" width="100%" height={height}>
      <defs>
        <filter id="fog-blur">
          <feGaussianBlur stdDeviation="8" />
        </filter>
      </defs>
      {segments.map((seg, i) => (
        <rect
          key={i}
          x={seg.x}
          y={0}
          width={seg.width}
          height={height}
          fill={`rgba(100, 100, 100, ${seg.density * 0.5})`}
          filter="url(#fog-blur)"
        />
      ))}
    </svg>
  );
}
