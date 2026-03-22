"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { api } from "@/lib/api";
import type { Entity, EntityGraph as EntityGraphType, EntityRelationship } from "@/types/entity";

interface Props {
  dossierSlug: string;
}

const ENTITY_COLORS: Record<string, string> = {
  company: "#3B82F6",
  person: "#F97316",
  regulator: "#EF4444",
  investor: "#10B981",
  sector: "#8B5CF6",
  legal_body: "#6B7280",
};

const ENTITY_SIZES: Record<string, number> = {
  company: 12,
  person: 10,
  regulator: 11,
  investor: 10,
  sector: 9,
  legal_body: 9,
};

const REL_STYLES: Record<string, string> = {
  ownership: "5,5",
  regulatory: "none",
  legal: "8,3",
  financial: "none",
  employment: "3,3",
  partnership: "10,5",
  competitor: "2,2",
  subsidiary: "none",
  investor: "none",
};

interface SimNode extends Entity {
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export function EntityGraph({ dossierSlug }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graph, setGraph] = useState<EntityGraphType | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .getEntityGraph(dossierSlug)
      .then(setGraph)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [dossierSlug]);

  useEffect(() => {
    if (!svgRef.current || !graph || graph.entities.length === 0) return;

    const width = 450;
    const height = 380;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("width", width).attr("height", height);

    // Build simulation data
    const nodes: SimNode[] = graph.entities.map((e) => ({ ...e }));
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));

    const links = graph.relationships
      .filter((r) => nodeMap.has(r.source_entity_id) && nodeMap.has(r.target_entity_id))
      .map((r) => ({
        source: r.source_entity_id,
        target: r.target_entity_id,
        type: r.relationship_type,
        weight: r.weight,
      }));

    // Force simulation
    const simulation = d3
      .forceSimulation(nodes as any)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance((d: any) => 100 - d.weight * 40)
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(25));

    // Zoom
    const zoomGroup = svg.append("g");

    svg.call(
      d3
        .zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.3, 5])
        .on("zoom", (event) => zoomGroup.attr("transform", event.transform))
    );

    // Links
    const link = zoomGroup
      .append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#333")
      .attr("stroke-width", (d: any) => 1 + d.weight * 2)
      .attr("stroke-dasharray", (d: any) => REL_STYLES[d.type] || "none")
      .attr("opacity", 0.6);

    // Link labels
    const linkLabel = zoomGroup
      .append("g")
      .selectAll("text")
      .data(links)
      .enter()
      .append("text")
      .attr("fill", "#444")
      .attr("font-size", "8px")
      .attr("text-anchor", "middle")
      .text((d: any) => d.type);

    // Nodes
    const node = zoomGroup
      .append("g")
      .selectAll("g")
      .data(nodes)
      .enter()
      .append("g")
      .style("cursor", "pointer")
      .on("click", (_event, d) => setSelectedEntity(d))
      .call(
        d3
          .drag<SVGGElement, SimNode>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }) as any
      );

    // Node circles
    node
      .append("circle")
      .attr("r", (d) => ENTITY_SIZES[d.entity_type] || 10)
      .attr("fill", (d) => ENTITY_COLORS[d.entity_type] || "#666")
      .attr("stroke", "#0a0a0a")
      .attr("stroke-width", 2);

    // Node labels
    node
      .append("text")
      .text((d) => d.name.length > 15 ? d.name.slice(0, 13) + "..." : d.name)
      .attr("dx", (d) => (ENTITY_SIZES[d.entity_type] || 10) + 4)
      .attr("dy", 4)
      .attr("fill", "#aaa")
      .attr("font-size", "10px")
      .attr("pointer-events", "none");

    // Simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      linkLabel
        .attr("x", (d: any) => (d.source.x + d.target.x) / 2)
        .attr("y", (d: any) => (d.source.y + d.target.y) / 2);

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [graph]);

  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
      <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">
        Money Map — Entity Graph
      </h3>

      {loading ? (
        <div className="flex h-[380px] items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-[var(--accent-blue)] border-t-transparent" />
        </div>
      ) : !graph || graph.entities.length === 0 ? (
        <p className="py-16 text-center text-sm text-[var(--text-secondary)]">
          No entity data available yet. Build the dossier to extract entities.
        </p>
      ) : (
        <>
          <svg ref={svgRef} className="w-full" />

          {/* Legend */}
          <div className="mt-2 flex flex-wrap gap-2">
            {Object.entries(ENTITY_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-1">
                <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-xs capitalize text-[var(--text-secondary)]">{type}</span>
              </div>
            ))}
          </div>

          {/* Selected entity detail */}
          {selectedEntity && (
            <div className="mt-3 rounded border border-[var(--border)] bg-[var(--bg-secondary)] p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: ENTITY_COLORS[selectedEntity.entity_type] }}
                  />
                  <span className="font-medium text-[var(--text-primary)]">
                    {selectedEntity.name}
                  </span>
                  <span className="rounded bg-[var(--bg-card)] px-1.5 py-0.5 text-xs capitalize text-[var(--text-secondary)]">
                    {selectedEntity.entity_type}
                  </span>
                </div>
                <button
                  onClick={() => setSelectedEntity(null)}
                  className="text-xs text-[var(--text-secondary)]"
                >
                  ✕
                </button>
              </div>
              {selectedEntity.description && (
                <p className="mt-2 text-xs text-[var(--text-secondary)]">
                  {selectedEntity.description}
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
