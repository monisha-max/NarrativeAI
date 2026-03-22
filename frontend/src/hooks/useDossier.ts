"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Dossier } from "@/types/dossier";

export function useDossier(slug: string) {
  const [dossier, setDossier] = useState<Dossier | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .getDossier(slug)
      .then((data) => {
        if (!cancelled) setDossier(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  return { dossier, loading, error };
}
