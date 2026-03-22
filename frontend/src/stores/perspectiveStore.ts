import { create } from "zustand";
import { persist } from "zustand/middleware";

interface PerspectiveState {
  risk: number;
  stakeholder: string;
  sentiment: number;
  geography: number;
  depth: number;
  setRisk: (v: number) => void;
  setStakeholder: (v: string) => void;
  setSentiment: (v: number) => void;
  setGeography: (v: number) => void;
  setDepth: (v: number) => void;
  reset: () => void;
}

const defaults = {
  risk: 0.5,
  stakeholder: "investor",
  sentiment: 0.5,
  geography: 0.5,
  depth: 0.5,
};

export const usePerspectiveStore = create<PerspectiveState>()(
  persist(
    (set) => ({
      ...defaults,
      setRisk: (risk) => set({ risk }),
      setStakeholder: (stakeholder) => set({ stakeholder }),
      setSentiment: (sentiment) => set({ sentiment }),
      setGeography: (geography) => set({ geography }),
      setDepth: (depth) => set({ depth }),
      reset: () => set(defaults),
    }),
    { name: "narrativeai-perspective" }
  )
);
