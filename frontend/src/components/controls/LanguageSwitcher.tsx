"use client";

import { useUserStore } from "@/stores/userStore";

const LANGUAGES = [
  { code: "en", label: "English", native: "EN" },
  { code: "hi", label: "हिन्दी", native: "हि" },
  { code: "te", label: "తెలుగు", native: "తె" },
  { code: "ta", label: "தமிழ்", native: "த" },
  { code: "bn", label: "বাংলা", native: "বা" },
];

export function LanguageSwitcher() {
  const { language, setLanguage } = useUserStore();

  return (
    <div className="flex gap-1">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => setLanguage(lang.code)}
          className={`rounded-md px-2 py-1 text-xs font-medium transition-all ${
            language === lang.code
              ? "bg-[var(--accent-salmon)]/15 text-[var(--accent-salmon)] ring-1 ring-[var(--accent-salmon)]/30"
              : "text-[var(--text-muted)] hover:text-[var(--text-secondary)] hover:bg-white/[0.03]"
          }`}
          title={lang.label}
        >
          {lang.native}
        </button>
      ))}
    </div>
  );
}
