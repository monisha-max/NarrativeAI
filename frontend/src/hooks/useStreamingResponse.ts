"use client";

import { useCallback, useState } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function useStreamingResponse() {
  const [text, setText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);

  const stream = useCallback(async (slug: string, body: Record<string, unknown>) => {
    setText("");
    setIsStreaming(true);

    try {
      const response = await fetch(`${BASE_URL}/briefing/${slug}/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          setText((prev) => prev + chunk);
        }
      }
    } catch (err) {
      console.error("Streaming error:", err);
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return { text, isStreaming, stream, reset: () => setText("") };
}
