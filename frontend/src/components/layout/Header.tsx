"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard" },
  { href: "/market-pulse", label: "Market Pulse" },
  { href: "/chat", label: "AI Chat" },
  { href: "/debate", label: "Debate Arena" },
  { href: "/earnings", label: "Earnings" },
  { href: "/rumor-tracker", label: "Rumors" },
  { href: "/portfolio-impact", label: "Portfolio" },
  { href: "/search", label: "Dossiers" },
];

export function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();

  return (
    <header className="glass sticky top-0 z-50">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          {/* ET-style salmon accent bar */}
          <div className="flex h-8 items-center gap-2">
            <div className="h-full w-1 rounded-full bg-[var(--accent-salmon)]" />
            <div>
              <span className="text-xs font-medium tracking-widest text-[var(--accent-salmon)]">
                ET × AI
              </span>
              <p className="serif text-base font-bold leading-none tracking-tight">
                NarrativeAI
              </p>
            </div>
          </div>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-0.5 md:flex">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`relative rounded-lg px-3 py-1.5 text-[13px] font-medium transition-all ${
                  isActive
                    ? "text-[var(--accent-salmon)]"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/[0.03]"
                }`}
              >
                {item.label}
                {isActive && (
                  <span className="absolute bottom-0 left-1/2 h-0.5 w-4 -translate-x-1/2 rounded-full bg-[var(--accent-salmon)]" />
                )}
              </Link>
            );
          })}
          <div className="mx-2 h-4 w-px bg-[var(--border)]" />
          <Link
            href="/settings"
            className="rounded-lg px-3 py-1.5 text-[13px] text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
          >
            Settings
          </Link>
        </nav>

        {/* Mobile hamburger */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-[var(--text-secondary)] hover:bg-white/[0.05] md:hidden"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={mobileOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
          </svg>
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <nav className="border-t border-white/[0.05] px-4 py-2 md:hidden">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className="block rounded-lg px-3 py-2 text-sm text-[var(--text-secondary)] hover:bg-white/[0.03] hover:text-[var(--text-primary)]"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
