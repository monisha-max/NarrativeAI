"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useUserStore } from "@/stores/userStore";
import type { DeltaCard } from "@/types/delta";

export function useDelta(dossierSlug?: string) {
  const userId = useUserStore((s) => s.username);
  const [cards, setCards] = useState<DeltaCard[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);

    const fetch = dossierSlug
      ? api.getDelta(userId, dossierSlug).then((d) => [d])
      : api.getAllDeltas(userId).then((d) => d.cards || []);

    fetch
      .then(setCards)
      .catch(() => setCards([]))
      .finally(() => setLoading(false));
  }, [userId, dossierSlug]);

  return { cards, loading };
}
