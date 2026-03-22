"use client";

import { usePerspectiveStore } from "@/stores/perspectiveStore";

export function usePerspective() {
  const perspective = usePerspectiveStore();

  return {
    ...perspective,
    toApiParams: () => ({
      risk: perspective.risk,
      stakeholder: perspective.stakeholder,
      sentiment: perspective.sentiment,
      geography: perspective.geography,
      depth: perspective.depth,
    }),
  };
}
