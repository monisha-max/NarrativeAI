"use client";

import ReactMarkdown from "react-markdown";

interface Props {
  text: string;
  isStreaming: boolean;
}

export function StreamingResponse({ text, isStreaming }: Props) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-6">
      {text ? (
        <div className="ai-response text-sm leading-relaxed text-[var(--text-primary)]">
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="serif mb-3 mt-4 text-lg font-bold text-[var(--text-primary)]">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="mb-2 mt-4 text-base font-semibold text-[var(--accent-salmon)]">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="mb-1 mt-3 text-sm font-semibold text-[var(--text-primary)]">{children}</h3>
              ),
              p: ({ children }) => (
                <p className="mb-3 leading-relaxed text-[var(--text-secondary)]">{children}</p>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-[var(--text-primary)]">{children}</strong>
              ),
              ul: ({ children }) => (
                <ul className="mb-3 ml-4 space-y-1.5 text-[var(--text-secondary)]">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="mb-3 ml-4 list-decimal space-y-1.5 text-[var(--text-secondary)]">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="leading-relaxed">{children}</li>
              ),
              code: ({ children }) => (
                <code className="mono rounded bg-[var(--bg-secondary)] px-1.5 py-0.5 text-xs text-[var(--accent-salmon)]">
                  {children}
                </code>
              ),
              blockquote: ({ children }) => (
                <blockquote className="my-3 border-l-2 border-[var(--accent-salmon)] pl-4 italic text-[var(--text-muted)]">
                  {children}
                </blockquote>
              ),
              hr: () => <hr className="my-4 border-[var(--border)]" />,
              table: ({ children }) => (
                <div className="my-3 overflow-x-auto">
                  <table className="w-full text-xs">{children}</table>
                </div>
              ),
              th: ({ children }) => (
                <th className="border-b border-[var(--border)] px-3 py-2 text-left font-semibold text-[var(--text-primary)]">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="border-b border-[var(--border)] px-3 py-2 text-[var(--text-secondary)]">
                  {children}
                </td>
              ),
            }}
          >
            {text}
          </ReactMarkdown>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-[var(--text-muted)]">
          <div className="h-3 w-3 animate-spin rounded-full border border-[var(--accent-salmon)] border-t-transparent" />
          <span className="text-sm">Thinking...</span>
        </div>
      )}
      {isStreaming && (
        <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse rounded-full bg-[var(--accent-salmon)]" />
      )}
    </div>
  );
}
