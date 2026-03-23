"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { StreamingResponse } from "@/components/briefing/StreamingResponse";
import { useUserStore } from "@/stores/userStore";
import axios from "axios";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function EarningsPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const userType = useUserStore((s) => s.userType);

  useEffect(() => {
    axios.get(`${API}/earnings/companies`).then((r) => setCompanies(r.data.companies));
  }, []);

  const decode = async (symbol: string) => {
    setSelected(symbol);
    setLoading(true);
    setAnalysis(null);
    const r = await axios.get(`${API}/earnings/decode/${symbol}?user_type=${userType}`);
    setAnalysis(r.data);
    setLoading(false);
  };

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-4xl px-4 py-6">
        <h1 className="mb-2 text-2xl font-bold">Smart Earnings Decoder</h1>
        <p className="mb-6 text-sm text-[var(--text-secondary)]">
          AI instantly decodes quarterly results — adapted to your profile ({userType.replace("_", " ")}).
          Change your profile in <a href="/settings" className="text-[var(--accent-blue)] underline">Settings</a>.
        </p>

        {/* Company selector */}
        <div className="mb-6 flex flex-wrap gap-2">
          {companies.map((c) => (
            <button
              key={c.symbol}
              onClick={() => decode(c.symbol)}
              className={`rounded-lg border px-4 py-2 text-sm transition-colors ${
                selected === c.symbol
                  ? "border-[var(--accent-blue)] bg-[var(--accent-blue)]/10 text-[var(--accent-blue)]"
                  : "border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--accent-blue)]/30"
              }`}
            >
              <span className="font-medium">{c.symbol}</span>
              <span className="ml-1 text-xs text-[var(--text-secondary)]">{c.quarter}</span>
            </button>
          ))}
        </div>

        {/* Earnings data + AI analysis */}
        {loading && (
          <div className="flex items-center gap-3 rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-8">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--accent-blue)] border-t-transparent" />
            <span className="text-sm text-[var(--text-secondary)]">Decoding earnings...</span>
          </div>
        )}

        {analysis && !loading && (
          <div className="space-y-4">
            {/* Key numbers */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                { label: "Revenue", value: `₹${analysis.data.revenue.toLocaleString("en-IN")} Cr`, change: analysis.data.revenue_yoy },
                { label: "Net Profit", value: `₹${analysis.data.net_profit.toLocaleString("en-IN")} Cr`, change: analysis.data.net_profit_yoy },
                { label: "EBITDA Margin", value: `${analysis.data.ebitda_margin}%`, change: null },
                { label: "vs Estimate", value: analysis.data.analyst_estimate_beat ? "Beat" : "Missed", change: analysis.data.estimate_beat_pct },
              ].map((item) => (
                <div key={item.label} className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-3">
                  <p className="text-xs text-[var(--text-secondary)]">{item.label}</p>
                  <p className="text-lg font-bold">{item.value}</p>
                  {item.change !== null && (
                    <p className={`text-xs font-medium ${item.change >= 0 ? "text-green-400" : "text-red-400"}`}>
                      {item.change >= 0 ? "+" : ""}{item.change}%
                    </p>
                  )}
                </div>
              ))}
            </div>

            {/* Segments */}
            <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4">
              <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">Segment Breakdown</h3>
              <div className="space-y-2">
                {analysis.data.key_segments.map((seg: any) => (
                  <div key={seg.name} className="flex items-center justify-between">
                    <span className="text-sm">{seg.name}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-sm">₹{seg.revenue.toLocaleString("en-IN")} Cr</span>
                      <span className={`text-xs font-medium ${seg.growth >= 0 ? "text-green-400" : "text-red-400"}`}>
                        {seg.growth >= 0 ? "+" : ""}{seg.growth}%
                      </span>
                      <div className="h-2 w-20 rounded-full bg-[var(--bg-secondary)]">
                        <div
                          className="h-full rounded-full bg-[var(--accent-blue)]"
                          style={{ width: `${Math.min(Math.abs(seg.growth) * 5, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Analysis */}
            <div className="rounded-xl border border-[var(--accent-salmon)]/20 bg-gradient-to-r from-[var(--accent-salmon)]/[0.04] to-transparent p-6">
              <div className="mb-3 flex items-center gap-2">
                <div className="h-4 w-0.5 rounded-full bg-[var(--accent-salmon)]" />
                <h3 className="text-sm font-semibold text-[var(--accent-salmon)]">AI Analysis for {userType.replace("_", " ")}</h3>
              </div>
              <StreamingResponse text={analysis.analysis} isStreaming={false} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
