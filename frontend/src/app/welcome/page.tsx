"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useUserStore } from "@/stores/userStore";

const HEADLINES = [
  "Byju's raises $800M at $22B valuation",
  "Byju's acquires Aakash Educational for $1B",
  "Deloitte resigns as Byju's auditor",
  "Byju's delays FY21 results by 18 months",
  "Byju's lays off 2,500 employees",
  "Investors demand Byju Raveendran's removal",
  "Byju's net loss widens to ₹4,588 crore",
  "Prosus writes down Byju's investment to zero",
  "NCLT admits insolvency petition against Byju's",
  "Byju Raveendran removed from management",
  "NCLAT overturns NCLT order temporarily",
  "Supreme Court reinstates insolvency proceedings",
  "ED investigates Byju's foreign remittances",
  "Byju's valuation crashes from $22B to near zero",
  "BDO exits as Byju's auditor",
  "Byju's misses multiple filing deadlines",
  "BCCI files insolvency petition over unpaid dues",
  "Byju's creditors form committee",
  "Investors petition against founder's control",
  "Byju's revenue recognition questioned",
  "Multiple FIRs filed related to Byju's",
  "Staff report salary delays across Byju's",
  "Byju's shuts down multiple business units",
  "Peak XV marks down Byju's investment",
  "BlackRock slashes Byju's valuation",
  "Byju's faces ₹9,000 crore ED probe",
  "Parent company Think & Learn under scanner",
  "Byju's advisory board members resign",
  "Court orders freeze on Byju Raveendran's assets",
  "International creditors join NCLT proceedings",
  "Byju's student enrollment numbers decline",
  "Former employees file wage theft complaints",
  "Regulatory bodies tighten edtech oversight",
  "Byju's restructuring plan rejected",
  "Global investors cite Byju's as cautionary tale",
  "Byju's board composition questioned",
  "Multiple lawsuits filed across jurisdictions",
  "Byju's attempts settlement with BCCI",
  "Resolution professional takes charge",
  "The complete collapse of India's most valued startup",
  "Byju's case becomes landmark governance study",
  "Media investigation reveals governance failures",
  "Byju's foreign subsidiary transactions probed",
  "Banking partners reduce exposure to Byju's",
  "Byju's tries to raise emergency funding",
  "Byju's brand value collapses in market surveys",
  "Byju's — from unicorn to cautionary tale",
];

const USER_TYPES = [
  { id: "retail_investor", label: "Investor", emoji: "📈", desc: "I trade or invest in markets" },
  { id: "student", label: "Student", emoji: "🎓", desc: "Learning about business & finance" },
  { id: "founder", label: "Founder", emoji: "🚀", desc: "Building or running a company" },
  { id: "cfo", label: "Finance Pro", emoji: "💼", desc: "CFO, analyst, or finance role" },
  { id: "journalist", label: "Journalist", emoji: "📰", desc: "I cover business news" },
  { id: "policy", label: "Policy/Gov", emoji: "🏛️", desc: "Regulatory or policy role" },
];

const FEATURES = [
  { icon: "🧬", label: "Story DNA", desc: "Predict what happens next using archetype patterns", color: "#4a7cf7" },
  { icon: "🌫️", label: "Fog of War", desc: "See where information is thin — know what you don't know", color: "#94a3b8" },
  { icon: "🔇", label: "Silence Detection", desc: "When nothing happening IS the story", color: "#fbbf24" },
  { icon: "🌊", label: "Ripple Effects", desc: "How one story sends shockwaves across others", color: "#a78bfa" },
  { icon: "⚔️", label: "Bull vs Bear", desc: "AI debates both sides with real data", color: "#22c55e" },
  { icon: "🎯", label: "Portfolio Impact", desc: "See how news hits YOUR money, stock by stock", color: "#f97316" },
];

export default function WelcomePage() {
  const router = useRouter();
  const [phase, setPhase] = useState<"hook" | "reveal" | "profile" | "ready">("hook");
  const [scrollOffset, setScrollOffset] = useState(0);
  const { setUserType, setUsername } = useUserStore();
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [counter, setCounter] = useState(0);

  // Auto-scroll headlines
  useEffect(() => {
    const interval = setInterval(() => setScrollOffset((prev) => prev + 1), 80);
    return () => clearInterval(interval);
  }, []);

  // Animated counter for "47"
  useEffect(() => {
    if (phase !== "hook") return;
    const target = 47;
    const duration = 2000;
    const start = Date.now();
    const tick = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      setCounter(Math.floor(progress * target));
      if (progress < 1) requestAnimationFrame(tick);
    };
    const timer = setTimeout(tick, 800);
    return () => clearTimeout(timer);
  }, [phase]);

  // Auto-advance
  useEffect(() => {
    if (phase === "hook") {
      const timer = setTimeout(() => setPhase("reveal"), 5500);
      return () => clearTimeout(timer);
    }
  }, [phase]);

  const handleComplete = () => {
    if (selectedType) setUserType(selectedType);
    if (name) setUsername(name);
    router.push("/");
  };

  return (
    <div className="min-h-screen overflow-hidden" style={{ background: "var(--bg-primary)" }}>
      {/* Subtle animated background particles — deterministic positions to avoid hydration mismatch */}
      <div className="pointer-events-none fixed inset-0 z-0">
        {[...Array(20)].map((_, i) => {
          const left = ((i * 37 + 13) % 100);
          const top = ((i * 53 + 7) % 100);
          const dur = 4 + (i % 5);
          const del = (i * 0.3) % 3;
          return (
            <motion.div
              key={i}
              className="absolute h-1 w-1 rounded-full"
              style={{
                background: i % 3 === 0 ? "var(--accent-salmon)" : "var(--accent-blue)",
                opacity: 0.15,
                left: `${left}%`,
                top: `${top}%`,
              }}
              animate={{
                y: [0, -30, 0],
                opacity: [0.05, 0.2, 0.05],
              }}
              transition={{
                duration: dur,
                repeat: Infinity,
                delay: del,
                ease: "easeInOut",
              }}
            />
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        {/* ==========================================
            PHASE 1: THE HOOK — Headlines scroll
            ========================================== */}
        {phase === "hook" && (
          <motion.div
            key="hook"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.6 }}
            className="relative flex min-h-screen items-center justify-center"
          >
            <div className="relative w-full max-w-5xl px-8">
              {/* Scrolling headlines — left and right columns */}
              <div className="flex gap-4">
                {[0, 1].map((col) => (
                  <div key={col} className="relative h-[350px] flex-1 overflow-hidden">
                    <div
                      className="absolute w-full space-y-1.5"
                      style={{
                        transform: `translateY(-${scrollOffset * (col === 0 ? 1.8 : 1.2)}px)`,
                        transition: "transform 0.08s linear",
                      }}
                    >
                      {[...HEADLINES, ...HEADLINES, ...HEADLINES].slice(col * 15).map((h, i) => (
                        <div
                          key={i}
                          className="rounded-lg border border-white/[0.04] bg-white/[0.015] px-4 py-2.5 text-sm"
                          style={{ color: `rgba(241, 245, 249, ${0.15 + (i % 5) * 0.05})` }}
                        >
                          {h}
                        </div>
                      ))}
                    </div>
                    <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-[var(--bg-primary)] via-transparent to-[var(--bg-primary)]" />
                  </div>
                ))}
              </div>

              {/* Counter + tagline */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5, duration: 0.8 }}
                className="mt-10 text-center"
              >
                <p className="mono text-7xl font-bold" style={{ color: "var(--accent-salmon)" }}>
                  {counter}
                </p>
                <p className="mt-3 text-xl text-[var(--text-secondary)]">
                  articles. One story. Miss a week, you&apos;re lost.
                </p>
                <p className="mt-1 text-sm text-[var(--text-muted)]">
                  This is business news in 2026.
                </p>
              </motion.div>

              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 3.5 }}
                onClick={() => setPhase("reveal")}
                className="mx-auto mt-8 block text-sm text-[var(--accent-salmon)] hover:text-white transition-colors"
              >
                There&apos;s a better way →
              </motion.button>
            </div>
          </motion.div>
        )}

        {/* ==========================================
            PHASE 2: THE REVEAL
            ========================================== */}
        {phase === "reveal" && (
          <motion.div
            key="reveal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex min-h-screen flex-col items-center justify-center px-8"
          >
            {/* ET branding bar */}
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="mb-8 h-0.5 w-24 rounded-full bg-[var(--accent-salmon)]"
            />

            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="text-center"
            >
              <p className="mb-2 text-xs font-medium tracking-[0.3em] text-[var(--accent-salmon)]">
                THE ECONOMIC TIMES × AI
              </p>
              <h1 className="serif text-5xl font-bold leading-tight md:text-7xl">
                <span className="text-gradient">One</span> dossier.
                <br />
                <span className="text-[var(--text-secondary)]">Complete</span> understanding.
              </h1>
            </motion.div>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="mt-6 max-w-xl text-center text-base leading-relaxed text-[var(--text-secondary)]"
            >
              NarrativeAI replaces scattered articles with <span className="text-[var(--text-primary)]">living intelligence</span>.
              Every story has a DNA. Every silence is a signal. Every visit picks up where you left off.
            </motion.p>

            {/* Feature cards with stagger */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
              className="stagger-in mt-10 grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6"
            >
              {FEATURES.map((f) => (
                <div
                  key={f.label}
                  className="card-glow rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-4 text-center"
                >
                  <span className="text-2xl">{f.icon}</span>
                  <p className="mt-2 text-xs font-semibold" style={{ color: f.color }}>{f.label}</p>
                  <p className="mt-1 text-[10px] leading-tight text-[var(--text-muted)]">{f.desc}</p>
                </div>
              ))}
            </motion.div>

            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2 }}
              onClick={() => setPhase("profile")}
              className="mt-10 rounded-full border border-[var(--accent-salmon)]/30 bg-[var(--accent-salmon)]/10 px-8 py-3 text-sm font-medium text-[var(--accent-salmon)] transition-all hover:bg-[var(--accent-salmon)]/20 hover:shadow-lg hover:shadow-[var(--accent-salmon)]/10"
            >
              Tell me who you are →
            </motion.button>
          </motion.div>
        )}

        {/* ==========================================
            PHASE 3: PROFILE
            ========================================== */}
        {phase === "profile" && (
          <motion.div
            key="profile"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex min-h-screen flex-col items-center justify-center px-8"
          >
            <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="w-full max-w-lg">
              <div className="mb-1 h-0.5 w-12 rounded-full bg-[var(--accent-salmon)]" />
              <h2 className="serif mb-2 text-3xl font-bold">How do you read the markets?</h2>
              <p className="mb-8 text-sm text-[var(--text-muted)]">
                Same facts, different lens. This shapes how NarrativeAI thinks with you.
              </p>

              <div className="stagger-in grid grid-cols-2 gap-3 sm:grid-cols-3">
                {USER_TYPES.map((type) => (
                  <motion.button
                    key={type.id}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => setSelectedType(type.id)}
                    className={`rounded-xl border p-4 text-center transition-all ${
                      selectedType === type.id
                        ? "border-[var(--accent-salmon)] bg-[var(--accent-salmon)]/10 shadow-lg shadow-[var(--accent-salmon)]/5"
                        : "border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--border-light)]"
                    }`}
                  >
                    <span className="text-2xl">{type.emoji}</span>
                    <p className="mt-2 text-sm font-medium">{type.label}</p>
                    <p className="mt-1 text-[10px] text-[var(--text-muted)]">{type.desc}</p>
                  </motion.button>
                ))}
              </div>

              {selectedType && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="mt-6">
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name (optional)"
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--bg-card)] px-4 py-3 text-center text-sm text-white placeholder-[var(--text-muted)] focus:border-[var(--accent-salmon)] focus:outline-none"
                  />
                  <motion.button
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    onClick={() => setPhase("ready")}
                    className="mt-4 w-full rounded-full bg-[var(--accent-salmon)] py-3 text-sm font-semibold text-[var(--et-navy)] transition-all hover:shadow-lg hover:shadow-[var(--accent-salmon)]/20"
                  >
                    Build my intelligence layer →
                  </motion.button>
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        )}

        {/* ==========================================
            PHASE 4: THE ENTRANCE
            ========================================== */}
        {phase === "ready" && (
          <motion.div
            key="ready"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex min-h-screen flex-col items-center justify-center px-8"
          >
            {/* Expanding circle animation */}
            <motion.div
              initial={{ scale: 0, opacity: 0.5 }}
              animate={{ scale: 20, opacity: 0 }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className="pointer-events-none absolute h-10 w-10 rounded-full bg-[var(--accent-salmon)]"
            />

            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.8 }}
              className="text-center"
            >
              <p className="text-sm text-[var(--accent-salmon)]">
                {name ? `${name}, welcome.` : "Welcome."}
              </p>
              <h1 className="serif mt-3 text-5xl font-bold md:text-6xl">
                Articles are <span className="text-[var(--text-muted)]">dead</span>.
              </h1>
              <p className="serif mt-2 text-2xl text-[var(--accent-salmon)]">
                The dossier is alive.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5 }}
              className="mt-6 text-center"
            >
              <p className="text-xs tracking-widest text-[var(--text-muted)]">
                IT KNOWS WHAT YOU KNOW. IT SEES WHAT YOU DON&apos;T.
              </p>

              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 2 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleComplete}
                className="mt-8 rounded-full bg-[var(--accent-salmon)] px-10 py-3.5 text-sm font-bold tracking-wide text-[var(--et-navy)] transition-all hover:shadow-xl hover:shadow-[var(--accent-salmon)]/20"
              >
                ENTER NARRATIVEAI
              </motion.button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
