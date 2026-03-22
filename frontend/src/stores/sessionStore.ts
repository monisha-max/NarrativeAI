import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SessionState {
  lastReadEvents: Record<string, string[]>;
  lastVisited: Record<string, string>;
  markEventRead: (slug: string, eventId: string) => void;
  markVisited: (slug: string) => void;
  getUnreadCount: (slug: string, totalEventIds: string[]) => number;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      lastReadEvents: {},
      lastVisited: {},
      markEventRead: (slug, eventId) =>
        set((state) => ({
          lastReadEvents: {
            ...state.lastReadEvents,
            [slug]: [...new Set([...(state.lastReadEvents[slug] || []), eventId])],
          },
        })),
      markVisited: (slug) =>
        set((state) => ({
          lastVisited: {
            ...state.lastVisited,
            [slug]: new Date().toISOString(),
          },
        })),
      getUnreadCount: (slug, totalEventIds) => {
        const read = get().lastReadEvents[slug] || [];
        return totalEventIds.filter((id) => !read.includes(id)).length;
      },
    }),
    { name: "narrativeai-session" }
  )
);
