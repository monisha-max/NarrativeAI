"use client";

import { Header } from "@/components/layout/Header";
import { PerspectiveDial } from "@/components/controls/PerspectiveDial";
import { LanguageSwitcher } from "@/components/controls/LanguageSwitcher";
import { useUserStore } from "@/stores/userStore";

const USER_TYPES = [
  { value: "student", label: "Student / Beginner", description: "Jargon explained, analogies used, concepts broken down" },
  { value: "retail_investor", label: "Retail Investor", description: "Portfolio impact, risk/reward framing, sector analysis" },
  { value: "founder", label: "Founder / Startup", description: "Competition, market-share, funding, regulatory compliance" },
  { value: "cfo", label: "CFO / Finance Pro", description: "Balance sheet, valuation, margins, compliance burden" },
  { value: "policy", label: "Policy / Regulator", description: "Regulatory history, statutory framework, international comparison" },
  { value: "journalist", label: "Journalist", description: "Counter-narratives, silence signals, entity connections" },
];

export default function SettingsPage() {
  const { userType, setUserType, username, setUsername } = useUserStore();

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-2xl px-4 py-10">
        <h1 className="mb-2 text-2xl font-bold text-[var(--text-primary)]">Settings</h1>
        <p className="mb-8 text-sm text-[var(--text-secondary)]">
          Customize how NarrativeAI adapts to you. These settings control the explanation layer — the facts don&apos;t change, the analytical frame does.
        </p>

        {/* Profile */}
        <section className="mb-8">
          <h2 className="mb-3 text-lg font-semibold text-[var(--text-primary)]">Profile</h2>
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-sm text-[var(--text-secondary)]">Username</label>
              <input
                type="text"
                value={username || ""}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                className="w-full rounded-md border border-[var(--border)] bg-[var(--bg-secondary)] px-3 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent-blue)] focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-[var(--text-secondary)]">Language</label>
              <LanguageSwitcher />
            </div>
          </div>
        </section>

        {/* User type / Personalized cognition */}
        <section className="mb-8">
          <h2 className="mb-1 text-lg font-semibold text-[var(--text-primary)]">
            Personalized Cognition
          </h2>
          <p className="mb-4 text-sm text-[var(--text-secondary)]">
            Choose your profile to adjust how stories are explained to you.
          </p>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {USER_TYPES.map((type) => (
              <button
                key={type.value}
                onClick={() => setUserType(type.value)}
                className={`rounded-lg border p-3 text-left transition-colors ${
                  userType === type.value
                    ? "border-[var(--accent-blue)] bg-[var(--accent-blue)]/10"
                    : "border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--accent-blue)]/30"
                }`}
              >
                <p className="text-sm font-medium text-[var(--text-primary)]">{type.label}</p>
                <p className="mt-0.5 text-xs text-[var(--text-secondary)]">{type.description}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Perspective dial */}
        <section>
          <h2 className="mb-3 text-lg font-semibold text-[var(--text-primary)]">
            Default Perspective
          </h2>
          <PerspectiveDial />
        </section>
      </main>
    </div>
  );
}
