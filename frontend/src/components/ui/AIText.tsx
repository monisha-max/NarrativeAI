"use client";

import ReactMarkdown from "react-markdown";

interface Props {
  children: string;
  className?: string;
}

/**
 * Renders AI-generated text with proper markdown formatting.
 * Use this instead of raw text display for any Claude/LLM output.
 */
export function AIText({ children, className = "" }: Props) {
  if (!children) return null;

  return (
    <div className={`ai-text text-sm leading-relaxed ${className}`}>
      <ReactMarkdown
        components={{
          h1: ({ children }) => (
            <h1 className="serif mb-2 mt-3 text-base font-bold text-[var(--text-primary)]">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="mb-2 mt-3 text-sm font-semibold text-[var(--accent-salmon)]">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="mb-1 mt-2 text-sm font-semibold text-[var(--text-primary)]">{children}</h3>
          ),
          p: ({ children }) => (
            <p className="mb-2 text-[var(--text-secondary)]">{children}</p>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-[var(--text-primary)]">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="text-[var(--text-muted)]">{children}</em>
          ),
          ul: ({ children }) => (
            <ul className="mb-2 ml-4 list-disc space-y-1 text-[var(--text-secondary)]">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-2 ml-4 list-decimal space-y-1 text-[var(--text-secondary)]">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="leading-relaxed">{children}</li>
          ),
          code: ({ children }) => (
            <code className="mono rounded bg-[var(--bg-secondary)] px-1 py-0.5 text-xs text-[var(--accent-salmon)]">
              {children}
            </code>
          ),
          blockquote: ({ children }) => (
            <blockquote className="my-2 border-l-2 border-[var(--accent-salmon)]/50 pl-3 text-[var(--text-muted)]">
              {children}
            </blockquote>
          ),
          hr: () => <hr className="my-3 border-[var(--border)]" />,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
