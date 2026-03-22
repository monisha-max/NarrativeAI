import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UserState {
  username: string | null;
  userType: string;
  language: string;
  followedDossiers: string[];
  setUsername: (username: string) => void;
  setUserType: (type: string) => void;
  setLanguage: (lang: string) => void;
  followDossier: (slug: string) => void;
  unfollowDossier: (slug: string) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      username: null,
      userType: "retail_investor",
      language: "en",
      followedDossiers: [],
      setUsername: (username) => set({ username }),
      setUserType: (userType) => set({ userType }),
      setLanguage: (language) => set({ language }),
      followDossier: (slug) =>
        set((state) => ({
          followedDossiers: [...new Set([...state.followedDossiers, slug])],
        })),
      unfollowDossier: (slug) =>
        set((state) => ({
          followedDossiers: state.followedDossiers.filter((s) => s !== slug),
        })),
    }),
    { name: "narrativeai-user" }
  )
);
