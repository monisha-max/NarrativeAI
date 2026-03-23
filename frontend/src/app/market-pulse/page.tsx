"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { AIText } from "@/components/ui/AIText";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Index { name: string; value: number; change: number; change_pct: number; trend: string; }
interface Stock { symbol: string; price: number; change_pct: number; volume: string; }
interface Sector { name: string; change_pct: number; mood: string; }

export default function MarketPulsePage() {
  const [data, setData] = useState<any>(null);
  const [commentary, setCommentary] = useState("");
  const [sectorDive, setSectorDive] = useState<string | null>(null);
  const [sectorAnalysis, setSectorAnalysis] = useState("");
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    axios.get(`${API}/market-pulse/data`).then((r) => { setData(r.data); setLoading(false); });
    setAiLoading(true);
    axios.get(`${API}/market-pulse/ai-commentary`).then((r) => { setCommentary(r.data.commentary); setAiLoading(false); });
  }, []);

  const handleSectorDive = async (sector: string) => {
    setSectorDive(sector);
    setSectorAnalysis("Loading...");
    const r = await axios.post(`${API}/market-pulse/sector-deep-dive?sector=${sector}`);
    setSectorAnalysis(r.data.analysis);
  };

  if (loading) return <div className="min-h-screen"><Header /><div className="flex justify-center py-20"><div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--accent-blue)] border-t-transparent" /></div></div>;

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-7xl px-4 py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Market Pulse Live</h1>
            <p className="text-sm text-[var(--text-secondary)]">Real-time market intelligence with AI commentary</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
            <span className="text-xs text-green-500">LIVE</span>
          </div>
        </div>

        {/* Indices */}
        <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
          {data.indices.map((idx: Index) => (
            <div key={idx.name} className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
              <p className="text-xs text-[var(--text-secondary)]">{idx.name}</p>
              <p className="text-xl font-bold">{idx.value.toLocaleString("en-IN")}</p>
              <p className={`text-sm font-medium ${idx.change_pct >= 0 ? "text-green-400" : "text-red-400"}`}>
                {idx.change_pct >= 0 ? "+" : ""}{idx.change.toFixed(2)} ({idx.change_pct >= 0 ? "+" : ""}{idx.change_pct}%)
              </p>
            </div>
          ))}
        </div>

        {/* AI Commentary */}
        <div className="mb-6 rounded-xl border border-[var(--accent-salmon)]/20 bg-gradient-to-r from-[var(--accent-salmon)]/[0.04] to-transparent p-6">
          <div className="mb-3 flex items-center gap-2">
            <div className="h-4 w-0.5 rounded-full bg-[var(--accent-salmon)]" />
            <h2 className="text-sm font-semibold text-[var(--accent-salmon)]">AI Market Commentary</h2>
            {aiLoading && <span className="h-3 w-3 animate-spin rounded-full border border-[var(--accent-salmon)] border-t-transparent" />}
          </div>
          {commentary ? <AIText>{commentary}</AIText> : <p className="text-sm text-[var(--text-muted)]">Generating commentary...</p>}
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Top Gainers */}
          <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
            <h3 className="mb-3 text-sm font-medium text-green-400">Top Gainers</h3>
            <div className="space-y-2">
              {data.top_gainers.map((s: Stock) => (
                <div key={s.symbol} className="flex items-center justify-between">
                  <div>
                    <span className="font-medium text-sm">{s.symbol}</span>
                    <span className="ml-2 text-xs text-[var(--text-secondary)]">Vol: {s.volume}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm">₹{s.price.toLocaleString("en-IN")}</span>
                    <span className="ml-2 text-xs font-medium text-green-400">+{s.change_pct}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Losers */}
          <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
            <h3 className="mb-3 text-sm font-medium text-red-400">Top Losers</h3>
            <div className="space-y-2">
              {data.top_losers.map((s: Stock) => (
                <div key={s.symbol} className="flex items-center justify-between">
                  <div>
                    <span className="font-medium text-sm">{s.symbol}</span>
                    <span className="ml-2 text-xs text-[var(--text-secondary)]">Vol: {s.volume}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm">₹{s.price.toLocaleString("en-IN")}</span>
                    <span className="ml-2 text-xs font-medium text-red-400">{s.change_pct}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* FII/DII */}
          <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
            <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">FII / DII Flow</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">FII Net</span>
                <span className={`font-medium text-sm ${data.fii_dii.fii_net < 0 ? "text-red-400" : "text-green-400"}`}>
                  ₹{Math.abs(data.fii_dii.fii_net).toLocaleString("en-IN")} Cr ({data.fii_dii.fii_trend})
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">DII Net</span>
                <span className={`font-medium text-sm ${data.fii_dii.dii_net > 0 ? "text-green-400" : "text-red-400"}`}>
                  ₹{data.fii_dii.dii_net.toLocaleString("en-IN")} Cr ({data.fii_dii.dii_trend})
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Sector Heatmap */}
        <div className="mt-6 rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
          <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">Sector Heatmap — Click for AI Deep Dive</h3>
          <div className="grid grid-cols-4 gap-2 sm:grid-cols-8">
            {data.sectors.map((s: Sector) => (
              <button
                key={s.name}
                onClick={() => handleSectorDive(s.name)}
                className={`rounded-lg p-3 text-center transition-all hover:scale-105 ${
                  sectorDive === s.name ? "ring-2 ring-[var(--accent-blue)]" : ""
                }`}
                style={{
                  backgroundColor: s.change_pct > 0
                    ? `rgba(16, 185, 129, ${Math.min(Math.abs(s.change_pct) / 2, 0.4)})`
                    : `rgba(239, 68, 68, ${Math.min(Math.abs(s.change_pct) / 2, 0.4)})`,
                }}
              >
                <p className="text-xs font-medium">{s.name}</p>
                <p className={`text-sm font-bold ${s.change_pct >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {s.change_pct >= 0 ? "+" : ""}{s.change_pct}%
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Sector Deep Dive */}
        {sectorDive && (
          <div className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-6">
            <h3 className="mb-3 font-semibold">{sectorDive} Sector Deep Dive</h3>
            <AIText>{sectorAnalysis}</AIText>
          </div>
        )}
      </main>
    </div>
  );
}
