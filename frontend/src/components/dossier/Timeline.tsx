"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import type { DossierEvent } from "@/types/dossier";
import { EVENT_TYPE_COLORS, EVENT_TYPE_LABELS } from "@/lib/constants";
import { fogDensityToOpacity, formatDate } from "@/lib/utils";

interface Props {
  events: DossierEvent[];
}

export function Timeline({ events }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [selectedEvent, setSelectedEvent] = useState<DossierEvent | null>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || events.length === 0) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = 420;
    const margin = { top: 40, right: 30, bottom: 50, left: 40 };

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("width", width).attr("height", height).attr("viewBox", `0 0 ${width} ${height}`);

    const parsedEvents = events.map((e) => ({
      ...e,
      date: new Date(e.occurred_at),
    }));

    // Time scale
    const timeExtent = d3.extent(parsedEvents, (d) => d.date) as [Date, Date];
    const xScale = d3
      .scaleTime()
      .domain(timeExtent)
      .range([margin.left, width - margin.right]);

    // Event type lanes
    const eventTypes = ["corporate", "regulatory", "financial", "management", "market", "legal"];
    const yScale = d3
      .scaleBand()
      .domain(eventTypes)
      .range([margin.top, height - margin.bottom])
      .padding(0.3);

    // Defs for fog and glow effects
    const defs = svg.append("defs");

    // Fog blur filter
    const fogFilter = defs.append("filter").attr("id", "fog-blur");
    fogFilter.append("feGaussianBlur").attr("stdDeviation", "6").attr("in", "SourceGraphic");

    // Glow filter for selected events
    const glowFilter = defs.append("filter").attr("id", "glow");
    glowFilter.append("feGaussianBlur").attr("stdDeviation", "3").attr("result", "coloredBlur");
    const glowMerge = glowFilter.append("feMerge");
    glowMerge.append("feMergeNode").attr("in", "coloredBlur");
    glowMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Background grid
    svg
      .append("g")
      .attr("class", "grid")
      .selectAll("line")
      .data(eventTypes)
      .enter()
      .append("line")
      .attr("x1", margin.left)
      .attr("x2", width - margin.right)
      .attr("y1", (d) => (yScale(d) || 0) + yScale.bandwidth() / 2)
      .attr("y2", (d) => (yScale(d) || 0) + yScale.bandwidth() / 2)
      .attr("stroke", "#1a1a1a")
      .attr("stroke-dasharray", "2,4");

    // Lane labels
    svg
      .append("g")
      .selectAll("text")
      .data(eventTypes)
      .enter()
      .append("text")
      .attr("x", margin.left - 5)
      .attr("y", (d) => (yScale(d) || 0) + yScale.bandwidth() / 2)
      .attr("text-anchor", "end")
      .attr("dominant-baseline", "middle")
      .attr("fill", "#555")
      .attr("font-size", "9px")
      .text((d) => EVENT_TYPE_LABELS[d]?.split(" ")[0] || d);

    // Fog of War overlay — render fog rectangles behind events
    const fogGroup = svg.append("g").attr("class", "fog-layer");

    // Group events by time segments and compute fog per segment
    const segmentWidth = Math.max((width - margin.left - margin.right) / 20, 30);
    const timeSegments: { x: number; fog: number }[] = [];

    for (let i = 0; i < 20; i++) {
      const segStart = margin.left + i * segmentWidth;
      const segEnd = segStart + segmentWidth;
      const tStart = xScale.invert(segStart);
      const tEnd = xScale.invert(segEnd);

      const segEvents = parsedEvents.filter((e) => e.date >= tStart && e.date <= tEnd);
      const avgFog =
        segEvents.length > 0
          ? segEvents.reduce((sum, e) => sum + e.fog_density, 0) / segEvents.length
          : 0.8; // No events = high fog

      timeSegments.push({ x: segStart, fog: avgFog });
    }

    fogGroup
      .selectAll("rect")
      .data(timeSegments)
      .enter()
      .append("rect")
      .attr("x", (d) => d.x)
      .attr("y", margin.top - 10)
      .attr("width", segmentWidth)
      .attr("height", height - margin.top - margin.bottom + 20)
      .attr("fill", (d) => `rgba(80, 80, 80, ${d.fog * 0.3})`)
      .attr("filter", "url(#fog-blur)")
      .attr("pointer-events", "none");

    // Connecting lines between sequential events
    const sortedEvents = [...parsedEvents].sort((a, b) => a.date.getTime() - b.date.getTime());
    for (let i = 1; i < sortedEvents.length; i++) {
      const prev = sortedEvents[i - 1];
      const curr = sortedEvents[i];
      svg
        .append("line")
        .attr("x1", xScale(prev.date))
        .attr("y1", (yScale(prev.event_type) || 0) + yScale.bandwidth() / 2)
        .attr("x2", xScale(curr.date))
        .attr("y2", (yScale(curr.event_type) || 0) + yScale.bandwidth() / 2)
        .attr("stroke", "#222")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "3,3")
        .attr("opacity", 0.5);
    }

    // Event nodes
    const nodes = svg
      .selectAll(".event-node")
      .data(parsedEvents)
      .enter()
      .append("g")
      .attr("class", "event-node")
      .attr("transform", (d) => {
        const x = xScale(d.date);
        const y = (yScale(d.event_type) || margin.top) + yScale.bandwidth() / 2;
        return `translate(${x},${y})`;
      })
      .style("opacity", (d) => fogDensityToOpacity(d.fog_density))
      .style("cursor", "pointer")
      .on("click", (_event, d) => setSelectedEvent(d));

    // Outer ring for market impact
    nodes
      .append("circle")
      .attr("r", (d) => 8 + Math.abs(d.market_impact || 0) * 6)
      .attr("fill", "none")
      .attr("stroke", (d) => EVENT_TYPE_COLORS[d.event_type] || "#666")
      .attr("stroke-width", 1)
      .attr("stroke-opacity", 0.3);

    // Main circle
    nodes
      .append("circle")
      .attr("r", 6)
      .attr("fill", (d) => EVENT_TYPE_COLORS[d.event_type] || "#666")
      .attr("stroke", "#0a0a0a")
      .attr("stroke-width", 2);

    // X axis
    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(
        d3.axisBottom(xScale)
          .ticks(d3.timeMonth.every(3) as any)
          .tickFormat(d3.timeFormat("%b %Y") as any)
      )
      .attr("color", "#555")
      .selectAll("text")
      .attr("font-size", "10px");

    // Zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([1, 8])
      .translateExtent([[0, 0], [width, height]])
      .on("zoom", (event) => {
        const newX = event.transform.rescaleX(xScale);

        svg.selectAll<SVGGElement, typeof parsedEvents[0]>(".event-node").attr("transform", (d) => {
          const x = newX(d.date);
          const y = (yScale(d.event_type) || margin.top) + yScale.bandwidth() / 2;
          return `translate(${x},${y})`;
        });

        svg.select<SVGGElement>("g:last-of-type").call(
          d3.axisBottom(newX)
            .ticks(6)
            .tickFormat(d3.timeFormat("%b %Y") as any) as any
        );
      });

    svg.call(zoom);
  }, [events]);

  if (events.length === 0) {
    return (
      <div className="flex h-[420px] items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--bg-card)]">
        <p className="text-[var(--text-secondary)]">No events yet. Build a dossier to see the timeline.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div
        ref={containerRef}
        className="relative rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4"
      >
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-medium text-[var(--text-secondary)]">
            Timeline — {events.length} events
          </h3>
          <div className="flex items-center gap-3 text-xs text-[var(--text-secondary)]">
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-4 rounded bg-gradient-to-r from-transparent to-gray-500/30" />
              Fog of War
            </span>
            <span>Scroll to zoom</span>
          </div>
        </div>
        <svg ref={svgRef} className="w-full" />
        <div ref={tooltipRef} />
      </div>

      {/* Event type legend */}
      <div className="flex flex-wrap gap-3">
        {Object.entries(EVENT_TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5">
            <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-xs text-[var(--text-secondary)]">
              {EVENT_TYPE_LABELS[type] || type}
            </span>
          </div>
        ))}
      </div>

      {/* Selected event detail */}
      {selectedEvent && (
        <div className="rounded-lg border border-[var(--accent-blue)]/30 bg-[var(--bg-card)] p-4">
          <div className="flex items-start justify-between">
            <div>
              <span
                className="rounded-full px-2 py-0.5 text-xs font-medium"
                style={{
                  color: EVENT_TYPE_COLORS[selectedEvent.event_type],
                  backgroundColor: `${EVENT_TYPE_COLORS[selectedEvent.event_type]}20`,
                }}
              >
                {EVENT_TYPE_LABELS[selectedEvent.event_type]}
              </span>
              <h4 className="mt-2 font-medium text-[var(--text-primary)]">
                {selectedEvent.title}
              </h4>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                {formatDate(selectedEvent.occurred_at)}
              </p>
            </div>
            <button
              onClick={() => setSelectedEvent(null)}
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            >
              ✕
            </button>
          </div>
          <p className="mt-3 text-sm leading-relaxed text-[var(--text-primary)]">
            {selectedEvent.summary}
          </p>
          {selectedEvent.entities_involved && selectedEvent.entities_involved.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {selectedEvent.entities_involved.map((entity) => (
                <span
                  key={entity}
                  className="rounded bg-[var(--bg-secondary)] px-2 py-0.5 text-xs text-[var(--text-secondary)]"
                >
                  {entity}
                </span>
              ))}
            </div>
          )}
          {selectedEvent.fog_density > 0.5 && (
            <div className="mt-3 rounded border border-[var(--accent-amber)]/20 bg-[var(--accent-amber)]/5 p-2">
              <p className="text-xs text-[var(--accent-amber)]">
                High fog density ({Math.round(selectedEvent.fog_density * 100)}%) — Information in this area is based on limited sources. Exercise caution.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
