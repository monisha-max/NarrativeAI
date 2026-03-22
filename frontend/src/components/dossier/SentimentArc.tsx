"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import type { DossierEvent } from "@/types/dossier";

interface Props {
  events: DossierEvent[];
}

export function SentimentArc({ events }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || events.length === 0) return;

    const eventsWithSentiment = events.filter((e) => e.sentiment_scores);
    if (eventsWithSentiment.length === 0) return;

    const width = 400;
    const height = 200;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("width", width).attr("height", height);

    const xScale = d3
      .scaleTime()
      .domain(d3.extent(eventsWithSentiment, (d) => new Date(d.occurred_at)) as [Date, Date])
      .range([margin.left, width - margin.right]);

    const yScale = d3.scaleLinear().domain([-1, 1]).range([height - margin.bottom, margin.top]);

    // Zero line
    svg
      .append("line")
      .attr("x1", margin.left)
      .attr("x2", width - margin.right)
      .attr("y1", yScale(0))
      .attr("y2", yScale(0))
      .attr("stroke", "#333")
      .attr("stroke-dasharray", "4,4");

    // Market confidence line
    const line = d3
      .line<(typeof eventsWithSentiment)[0]>()
      .x((d) => xScale(new Date(d.occurred_at)))
      .y((d) => yScale(d.sentiment_scores!.market_confidence))
      .curve(d3.curveMonotoneX);

    svg
      .append("path")
      .datum(eventsWithSentiment)
      .attr("fill", "none")
      .attr("stroke", "#3B82F6")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Axes
    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(xScale).ticks(4).tickFormat(d3.timeFormat("%b") as any))
      .attr("color", "#666");

    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale).ticks(5))
      .attr("color", "#666");
  }, [events]);

  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
      <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">Sentiment Arc</h3>
      {events.filter((e) => e.sentiment_scores).length === 0 ? (
        <p className="py-8 text-center text-sm text-[var(--text-secondary)]">
          No sentiment data available
        </p>
      ) : (
        <svg ref={svgRef} className="w-full" />
      )}
    </div>
  );
}
